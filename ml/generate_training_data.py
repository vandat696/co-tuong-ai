import os
import sys
import numpy as np
import random
import time

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.board import Board
from engines.v3.engine import AIEngineV3
from engines.v3.halfkp import active_features, NUM_FEATURES_PER_SIDE
from engines.v3.move import source_square, target_square

def generate_self_play_games(num_games=10, max_moves=200):
    """
    Generates training data via V3 self-play.
    """
    dataset_features_red = []
    dataset_features_black = []
    dataset_scores = []
    dataset_results = []
    
    print(f"Starting generation of {num_games} games...")
    start_time = time.time()
    
    for game_idx in range(num_games):
        board = Board()
        engine = AIEngineV3(board, max_depth=3, time_limit=0.1) # Fast search for generation
        engine.context.start() # Ensure position is initialized
        
        game_history = []
        is_red_turn = True
        result = 0.5 # Draw by default
        
        for move_idx in range(max_moves):
            # To add variety, make the first few moves random
            if move_idx < 4:
                moves = engine.context.legal_moves(is_red_turn)
                if not moves:
                    result = -1.0 if is_red_turn else 1.0
                    break
                best_move = random.choice(moves)
                eval_score = 0 # Ignore score for random moves
            else:
                # Use engine to find best move and score
                try:
                    best_move = engine.search_best_move(is_red_turn)
                    eval_score = engine.root_best_score
                    if not is_red_turn:
                        eval_score = -eval_score # Convert to absolute Red perspective score
                except Exception as e:
                    print(f"Engine error: {e}")
                    break
                    
            if not best_move:
                # No valid moves -> loss for current player
                result = 0.0 if is_red_turn else 1.0
                break
                
            # Extract features before making the move
            squares = [piece for row in board.board for piece in row]
            red_king = None
            black_king = None
            for sq, piece in enumerate(squares):
                if piece == Board.RED_KING: red_king = sq
                elif piece == Board.BLACK_KING: black_king = sq
                
            if red_king is not None and black_king is not None:
                red_feats, black_feats = active_features(squares, red_king, black_king)
                game_history.append((red_feats, black_feats, eval_score))
                
            # Make move
            from_row, from_col = divmod(source_square(best_move), 9)
            to_row, to_col = divmod(target_square(best_move), 9)
            board.move_piece(from_row, from_col, to_row, to_col)
            
            # Check draw or repetition
            # ... simple check ...
            
            is_red_turn = not is_red_turn
            
        print(f"Game {game_idx+1}/{num_games} finished in {len(game_history)} moves. Result: {result}")
        
        # Target blending: 50% game result, 50% engine evaluation
        # Engine evaluation is in centipawns. Convert to [0, 1] WDL scale:
        # WDL = 1 / (1 + 10^(-score / 400))  (standard chess formula)
        
        for r_feat, b_feat, score in game_history:
            wdl_score = 1.0 / (1.0 + 10 ** (-score / 400.0))
            blended_target = 0.5 * result + 0.5 * wdl_score
            
            dataset_features_red.append(r_feat)
            dataset_features_black.append(b_feat)
            dataset_scores.append(blended_target)
            dataset_results.append(result)
            
    print(f"Generated {len(dataset_scores)} positions in {time.time() - start_time:.2f}s")
    
    # Save to disk
    os.makedirs('ml/dataset', exist_ok=True)
    np.savez_compressed(
        'ml/dataset/self_play_data.npz',
        features_red=np.array(dataset_features_red, dtype=object),
        features_black=np.array(dataset_features_black, dtype=object),
        targets=np.array(dataset_scores, dtype=np.float32)
    )
    print("Saved to ml/dataset/self_play_data.npz")

if __name__ == "__main__":
    generate_self_play_games(num_games=10) # Small batch for testing
