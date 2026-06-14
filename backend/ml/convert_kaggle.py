"""Script to convert Kaggle Xiangqi dataset to NNUE training format."""

import csv
import sys
import os
import numpy as np
from tqdm import tqdm
from collections import defaultdict

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.v3.context import SearchContext
from engines.v3.move import move_to_coordinates
from engines.v3.halfkp import active_features
from core.board import Board

def parse_kaggle_move(context, legal_moves, move_str, is_red):
    piece_chars = {1:'K', 2:'A', 3:'E', 4:'R', 5:'H', 6:'C', 7:'P'}
    
    candidates = []
    for m in legal_moves:
        from_row, from_col, to_row, to_col = move_to_coordinates(m)
        source = from_row * 9 + from_col
        piece = context.position.squares[source]
        kind = abs(piece)
        
        # 1. Check piece type
        if move_str[0].upper() != piece_chars[kind]:
            continue
            
        # 2. Check action
        advance = (to_row < from_row) if is_red else (to_row > from_row)
        retreat = (to_row > from_row) if is_red else (to_row < from_row)
        horizontal = (to_row == from_row)
        
        action_char = move_str[2]
        if action_char == '+' and not advance: continue
        if action_char == '-' and not retreat: continue
        if action_char == '.' and not horizontal: continue
        
        # 3. Check target / steps
        end_char = move_str[3]
        target_f = 9 - to_col if is_red else to_col + 1
        if action_char == '.':
            if str(target_f) != end_char: continue
        else:
            if kind in [Board.RED_HORSE, Board.RED_ELEPHANT, Board.RED_ADVISOR]:
                if str(target_f) != end_char: continue
            else:
                steps = abs(to_row - from_row)
                if str(steps) != end_char: continue
                
        candidates.append(m)
        
    if len(candidates) == 1:
        return candidates[0]
        
    if len(candidates) > 1:
        start_char = move_str[1]
        
        # If it's + (front) or - (back)
        if start_char in ['+', '-']:
            candidates.sort(key=lambda m: move_to_coordinates(m)[0], reverse=not is_red)
            if start_char == '+':
                return candidates[0]
            else:
                return candidates[-1]
                
        # If it's a digit
        for m in candidates:
            from_row, from_col, to_row, to_col = move_to_coordinates(m)
            start_f = 9 - from_col if is_red else from_col + 1
            if str(start_f) == start_char:
                return m
                
    return None

def get_outcome_value(winner):
    if winner == 'red':
        return 1.0
    elif winner == 'black':
        return 0.0
    return 0.5

def parse_dataset(dataset_dir, output_file, max_games=None):
    gameinfo_path = os.path.join(dataset_dir, 'gameinfo.csv')
    moves_path = os.path.join(dataset_dir, 'moves.csv')
    
    print("Reading gameinfo.csv...")
    game_outcomes = {}
    if os.path.exists(gameinfo_path):
        with open(gameinfo_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                game_id = row.get('gameID')
                if game_id and 'winner' in row:
                    if row['winner'] == 'red':
                        game_outcomes[game_id] = 1.0
                    elif row['winner'] == 'black':
                        game_outcomes[game_id] = 0.0
                    else:
                        game_outcomes[game_id] = 0.5
            
    print("Reading moves.csv...")
    games_raw = defaultdict(list)
    with open(moves_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            games_raw[row['gameID']].append((int(row['turn']), row['side'], row['move']))
            
    games = {}
    for gid, moves in games_raw.items():
        # Sort by turn, then red comes before black
        # 'red' > 'black' alphabetically? No, we want 'red' first.
        # So key=(turn, 0 if side=='red' else 1)
        moves.sort(key=lambda x: (x[0], 0 if x[1] == 'red' else 1))
        games[gid] = [m[2] for m in moves]
            
    game_ids = list(games.keys())
    if max_games and max_games < len(game_ids):
        game_ids = game_ids[:max_games]
        
    print(f"Processing {len(game_ids)} games...")
    
    us_features_list = []
    them_features_list = []
    values_list = []
    
    processed_games = 0
    skipped_games = 0
    
    for game_id in tqdm(game_ids):
        outcome = game_outcomes.get(game_id, 0.5)
        moves = games[game_id]
        
        board = Board()
        context = SearchContext(board, 1.0)
        context.start()
        
        is_red_turn = True
        valid_game = True
        
        game_us_features = []
        game_them_features = []
        game_values = []
        
        for move_str in moves:
            legal_moves = context.position.generate_moves(is_red_turn)
            matched_move = parse_kaggle_move(context, legal_moves, move_str, is_red_turn)
            
            if matched_move is None:
                # If we cannot parse the move, skip the entire game to ensure data purity
                print(f"Cannot parse move '{move_str}' in game {game_id}")
                valid_game = False
                break
                
            # Extract features before making the move
            red_king = context.position.king_squares[True]
            black_king = context.position.king_squares[False]
            red_f, black_f = active_features(context.position.squares, red_king, black_king)
            
            # Padded features to length 32
            rf_padded = np.zeros(32, dtype=np.int16)
            bf_padded = np.zeros(32, dtype=np.int16)
            
            n_red = min(32, len(red_f))
            n_black = min(32, len(black_f))
            
            rf_padded[:n_red] = red_f[:n_red]
            bf_padded[:n_black] = black_f[:n_black]
            
            if is_red_turn:
                game_us_features.append(rf_padded)
                game_them_features.append(bf_padded)
            else:
                game_us_features.append(bf_padded)
                game_them_features.append(rf_padded)
            
            # Use V3 heuristic to evaluate the position
            score_red = context.position.evaluate()
            # Target value is from the perspective of the side to move
            val = float(score_red if is_red_turn else -score_red)
            game_values.append(val)
            
            # Make move
            context.position.make_move(matched_move, is_red_turn)
            
            is_red_turn = not is_red_turn
            
        if valid_game:
            us_features_list.extend(game_us_features)
            them_features_list.extend(game_them_features)
            values_list.extend(game_values)
            processed_games += 1
        else:
            skipped_games += 1
            
    print(f"Finished processing. Successful: {processed_games}, Skipped: {skipped_games}")
    print(f"Total positions: {len(values_list)}")
    
    # Save to disk
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    np.savez_compressed(
        output_file,
        us_features=np.array(us_features_list),
        them_features=np.array(them_features_list),
        values=np.array(values_list, dtype=np.float32)
    )
    print(f"Dataset saved to {output_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert Kaggle dataset")
    parser.add_argument("--dataset_dir", type=str, default="ml/dataset", help="Dir containing gameinfo.csv and moves.csv")
    parser.add_argument("--output", type=str, default="ml/dataset/kaggle_data.npz", help="Output npz file")
    parser.add_argument("--max_games", type=int, default=None, help="Max games to process (for testing)")
    
    args = parser.parse_args()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    dataset_dir = os.path.join(base_dir, args.dataset_dir)
    output_file = os.path.join(base_dir, args.output)
    
    parse_dataset(dataset_dir, output_file, args.max_games)
