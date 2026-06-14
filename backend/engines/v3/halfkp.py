"""HalfKP feature encoding for NNUE."""

from core.board import Board

NUM_FEATURES_PER_SIDE = 1620
NUM_PIECE_TYPES = 18
NUM_SQUARES = 90

# Maps piece to an index 0-17.
# We exclude the King of the side we are calculating for, because the features
# are relative to the King's position (the "K" in HalfKP).
# Piece values:
# Red: King(1), Advisor(2), Elephant(3), Chariot(4), Horse(5), Cannon(6), Pawn(7)
# Black: King(-1), Advisor(-2), Elephant(-3), Chariot(-4), Horse(-5), Cannon(-6), Pawn(-7)
def get_piece_index(piece, perspective_is_red):
    # If perspective is red, we exclude red king (1).
    # If perspective is black, we exclude black king (-1).
    # We map the remaining 13 piece types to 0-13 (leaving room up to 17 for future extensions or padding).
    if piece == 0:
        return -1
        
    kind = abs(piece)
    is_red_piece = piece > 0
    
    # Exclude own king
    if perspective_is_red and piece == Board.RED_KING:
        return -1
    if not perspective_is_red and piece == Board.BLACK_KING:
        return -1
        
    # Mapping logic:
    # Own pieces: 0 to 5 (Advisor to Pawn)
    # Enemy king: 6
    # Enemy pieces: 7 to 12 (Advisor to Pawn)
    
    is_own_piece = (perspective_is_red and is_red_piece) or (not perspective_is_red and not is_red_piece)
    
    if is_own_piece:
        return kind - 2 # 2-7 -> 0-5
    else:
        if kind == Board.RED_KING: # Enemy king is 1
            return 6
        return kind + 5 # 2-7 -> 7-12

def feature_index(piece, square, king_square, perspective_is_red):
    """
    Calculates the feature index.
    To match the 1620 input size: 18 piece types * 90 squares.
    """
    p_idx = get_piece_index(piece, perspective_is_red)
    if p_idx == -1:
        return -1
        
    # Flip the board horizontally and vertically from Black's perspective
    # so that advancing means the same thing for the network.
    sq = square if perspective_is_red else 89 - square
    return p_idx * NUM_SQUARES + sq

def active_features(squares, king_sq_red, king_sq_black):
    """
    Returns (red_features, black_features) which are lists of active feature indices.
    """
    red_features = []
    black_features = []
    
    for sq, piece in enumerate(squares):
        if piece == Board.EMPTY:
            continue
            
        r_idx = feature_index(piece, sq, king_sq_red, True)
        if r_idx != -1:
            red_features.append(r_idx)
            
        b_idx = feature_index(piece, sq, king_sq_black, False)
        if b_idx != -1:
            black_features.append(b_idx)
            
    return red_features, black_features

def feature_diff(source, target, piece, captured, king_sq_red, king_sq_black):
    """
    Returns (removed_red, added_red, removed_black, added_black)
    """
    removed_red = []
    added_red = []
    removed_black = []
    added_black = []
    
    # 1. Piece moves from source to target
    r_idx_src = feature_index(piece, source, king_sq_red, True)
    if r_idx_src != -1: removed_red.append(r_idx_src)
    
    r_idx_dst = feature_index(piece, target, king_sq_red, True)
    if r_idx_dst != -1: added_red.append(r_idx_dst)
    
    b_idx_src = feature_index(piece, source, king_sq_black, False)
    if b_idx_src != -1: removed_black.append(b_idx_src)
    
    b_idx_dst = feature_index(piece, target, king_sq_black, False)
    if b_idx_dst != -1: added_black.append(b_idx_dst)
    
    # 2. Captured piece is removed from target
    if captured != Board.EMPTY:
        r_idx_cap = feature_index(captured, target, king_sq_red, True)
        if r_idx_cap != -1: removed_red.append(r_idx_cap)
        
        b_idx_cap = feature_index(captured, target, king_sq_black, False)
        if b_idx_cap != -1: removed_black.append(b_idx_cap)
        
    return removed_red, added_red, removed_black, added_black
