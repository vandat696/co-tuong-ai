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
    """Ánh xạ một quân cờ thành một chỉ số đặc trưng từ 0 đến 17 dựa trên góc nhìn của người chơi.

    Hàm này phân loại các quân cờ cho bộ mã hóa đặc trưng HalfKP. Nó bỏ qua
    Tướng của phe đang được đánh giá (vì Tướng đóng vai trò là điểm tham chiếu trung tâm).
    Các quân cờ của phe ta được ánh xạ từ 0-5, Tướng địch được ánh xạ là 6, và các quân
    của phe địch được ánh xạ từ 7-12.

    Args:
        piece (int): Giá trị số nguyên đại diện cho loại quân và màu sắc 
            (ví dụ: Board.RED_HORSE, Board.BLACK_CANNON).
        perspective_is_red (bool): True nếu đặc trưng đang được tính từ góc nhìn
            của phe Đỏ, False nếu từ góc nhìn của phe Đen.

    Returns:
        int: Chỉ số đã được ánh xạ cho quân cờ (0-17). Trả về -1 nếu là ô trống 
        hoặc là Tướng của phe đang được đánh giá.
    """
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
    """Tính toán chỉ số đặc trưng 1D cho một quân cờ nằm trên một ô cụ thể.

    Hàm này tính toán một chỉ số duy nhất cho sự kết hợp giữa quân cờ và ô cờ để sử dụng
    trong mảng đầu vào của NNUE. Tổng kích thước đầu vào là 1620 (18 loại quân * 90 ô).
    Hàm cũng xử lý việc lật bàn cờ theo chiều dọc đối với góc nhìn của quân Đen, để
    đảm bảo hướng tiến lên là đồng nhất cho cả hai bên.

    Args:
        piece (int): Giá trị số nguyên đại diện cho quân cờ.
        square (int): Chỉ số ô cờ (0-89) nơi quân cờ đang đứng.
        king_square (int): Chỉ số ô cờ của Tướng (giữ lại để tương thích với API của HalfKP, 
            mặc dù không thực sự được sử dụng trong cách triển khai Piece-Square đơn giản này).
        perspective_is_red (bool): True nếu tính từ góc nhìn của Đỏ, False nếu của Đen.

    Returns:
        int: Chỉ số đặc trưng được tính toán (0-1619). Trả về -1 nếu quân cờ không hợp lệ hoặc ô trống.
    """
    p_idx = get_piece_index(piece, perspective_is_red)
    if p_idx == -1:
        return -1
        
    # Flip the board horizontally and vertically from Black's perspective
    # so that advancing means the same thing for the network.
    sq = square if perspective_is_red else 89 - square
    return p_idx * NUM_SQUARES + sq

def active_features(squares, king_sq_red, king_sq_black):
    """Trích xuất tất cả các chỉ số đặc trưng đang kích hoạt cho trạng thái bàn cờ hiện tại.

    Duyệt qua toàn bộ các ô trên bàn cờ và tính toán các chỉ số đặc trưng đang kích hoạt
    cho cả góc nhìn của Đỏ và Đen. Hàm này thường được sử dụng để khởi tạo 
    bộ cộng dồn (accumulator) hoặc để tạo dữ liệu huấn luyện từ các thế cờ tĩnh.

    Args:
        squares (list[int]): Danh sách 90 số nguyên đại diện cho các quân cờ trên bàn.
        king_sq_red (int): Chỉ số ô cờ (0-89) của Tướng Đỏ.
        king_sq_black (int): Chỉ số ô cờ (0-89) của Tướng Đen.

    Returns:
        tuple[list[int], list[int]]: Một tuple chứa hai danh sách:
            - red_features: Các chỉ số đặc trưng kích hoạt từ góc nhìn của Đỏ.
            - black_features: Các chỉ số đặc trưng kích hoạt từ góc nhìn của Đen.
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
    """Tính toán sự thay đổi (deltas) của các đặc trưng khi một nước đi được thực hiện.

    Thay vì tính lại toàn bộ các đặc trưng từ đầu, hàm này xác định những 
    đặc trưng nào cần được thêm vào hoặc loại bỏ khỏi bộ cộng dồn (accumulator) khi một 
    quân cờ di chuyển từ `source` đến `target`, và có thể ăn một quân của đối phương.

    Args:
        source (int): Chỉ số ô cờ xuất phát (0-89) của quân cờ đang di chuyển.
        target (int): Chỉ số ô cờ đích đến (0-89) của quân cờ đang di chuyển.
        piece (int): Giá trị số nguyên của quân cờ đang di chuyển.
        captured (int): Giá trị số nguyên của quân cờ bị ăn, hoặc Board.EMPTY nếu không có.
        king_sq_red (int): Chỉ số ô cờ của Tướng Đỏ.
        king_sq_black (int): Chỉ số ô cờ của Tướng Đen.

    Returns:
        tuple[list[int], list[int], list[int], list[int]]: Một tuple gồm 4 danh sách:
            - removed_red: Các đặc trưng cần xóa khỏi bộ cộng dồn của Đỏ.
            - added_red: Các đặc trưng cần thêm vào bộ cộng dồn của Đỏ.
            - removed_black: Các đặc trưng cần xóa khỏi bộ cộng dồn của Đen.
            - added_black: Các đặc trưng cần thêm vào bộ cộng dồn của Đen.
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
