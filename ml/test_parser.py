import csv
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engines.v3.context import SearchContext
from engines.v3.move import move_to_coordinates
from core.board import Board

def to_algebraic(context, move, is_red):
    from_row, from_col, to_row, to_col = move_to_coordinates(move)
    source = from_row * 9 + from_col
    
    piece = context.position.squares[source]
    kind = abs(piece)
    
    # Piece char
    piece_chars = {1:'K', 2:'A', 3:'E', 4:'R', 5:'H', 6:'C', 7:'P'}
    char_0 = piece_chars[kind]
    if not is_red:
        char_0 = char_0.lower()
        
    # Start file
    if is_red:
        start_file = 9 - from_col
        end_file = 9 - to_col
        advance = (to_row < from_row)
        retreat = (to_row > from_row)
        row_diff = from_row - to_row
    else:
        start_file = from_col + 1
        end_file = to_col + 1
        advance = (to_row > from_row)
        retreat = (to_row < from_row)
        row_diff = to_row - from_row
        
    char_1 = str(start_file)
    
    # Action
    if advance:
        char_2 = '+'
    elif retreat:
        char_2 = '-'
    else:
        char_2 = '.'
        
    # End value
    if char_2 == '.':
        char_3 = str(end_file)
    else:
        if kind in [Board.RED_HORSE, Board.RED_ELEPHANT, Board.RED_ADVISOR]:
            char_3 = str(end_file)
        else:
            char_3 = str(abs(row_diff))
            
    return f"{char_0}{char_1}{char_2}{char_3}"

def main():
    board = Board()
    context = SearchContext(board, 1.0)
    context.start()
    
    # Target moves for game 57380690
    target_moves = [
        "C2.5", "h2+3", "H2+3", "c8.6", "R1.2", "h8+7", "P7+1", "r9.8", "C8.7"
    ]
    
    is_red = True
    for t in target_moves:
        legal_moves = context.position.generate_moves(is_red)
        found = False
        for m in legal_moves:
            alg = to_algebraic(context, m, is_red)
            if alg == t:
                print(f"Match: {t} -> {m}")
                context.position.make_move(m, is_red)
                found = True
                break
        
        if not found:
            print(f"FAILED to find {t}")
            print("Legal moves were:")
            for m in legal_moves:
                print("  ", to_algebraic(context, m, is_red))
            break
            
        is_red = not is_red

if __name__ == "__main__":
    main()
