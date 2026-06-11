"""
eval.py - Hàm đánh giá thế cờ (Evaluation function)
"""

from src.board import Board


class Evaluator:
    """Lớp đánh giá thế cờ"""
    
    # Điểm số của từng loại quân
    PIECE_VALUES = {
        Board.RED_KING: 6000,
        Board.RED_CHARIOT: 600,
        Board.RED_HORSE: 270,
        Board.RED_ELEPHANT: 120,
        Board.RED_CANNON: 285,
        Board.RED_ADVISOR: 120,
        Board.RED_PAWN: 30,
        
        Board.BLACK_KING: 6000,
        Board.BLACK_CHARIOT: 600,
        Board.BLACK_HORSE: 270,
        Board.BLACK_ELEPHANT: 120,
        Board.BLACK_CANNON: 285,
        Board.BLACK_ADVISOR: 120,
        Board.BLACK_PAWN: 30,
    }
    
    # Bảng vị trí (Piece-Square Tables) - Khuyến khích AI chiếm trung tâm
    # Góc nhìn của Đỏ (đi từ dưới lên). Cờ Đen sẽ lật ngược chỉ số hàng tự động.
    PAWN_PST = [
        [ 0,  3,  6,  9, 12,  9,  6,  3,  0], # Hàng 0: Đáy địch
        [ 0,  4,  8, 12, 16, 12,  8,  4,  0], # Hàng 1
        [ 0,  4,  8, 12, 16, 12,  8,  4,  0], # Hàng 2
        [ 0,  2,  4,  6,  8,  6,  4,  2,  0], # Hàng 3 (Đã qua sông)
        [ 0,  1,  2,  3,  4,  3,  2,  1,  0], # Hàng 4 (Đã qua sông)
        [-2,  0,  0,  0,  0,  0,  0,  0, -2], # Hàng 5 (Chưa qua sông, né góc)
        [-2,  0,  0,  0,  0,  0,  0,  0, -2],
        [-2,  0,  0,  0,  0,  0,  0,  0, -2],
        [-2,  0,  0,  0,  0,  0,  0,  0, -2],
        [-2,  0,  0,  0,  0,  0,  0,  0, -2],
    ]

    HORSE_PST = [
        [-4, -2, -2, -2, -2, -2, -2, -2, -4],
        [-2,  2,  4,  6,  6,  6,  4,  2, -2],
        [-2,  4,  6,  8,  8,  8,  6,  4, -2],
        [-2,  4,  6,  8,  8,  8,  6,  4, -2],
        [-2,  2,  4,  6,  6,  6,  4,  2, -2],
        [-2,  2,  4,  6,  6,  6,  4,  2, -2],
        [-2,  4,  6,  8,  8,  8,  6,  4, -2],
        [-2,  4,  6,  8,  8,  8,  6,  4, -2],
        [-2,  2,  4,  6,  6,  6,  4,  2, -2],
        [-4, -2, -2, -2, -2, -2, -2, -2, -4],
    ]

    CANNON_PST = [
        [ 6,  4,  0,-10,-12,-10,  0,  4,  6], # Hàng 0: Đáy địch
        [ 2,  2,  0, -4,-14, -4,  0,  2,  2], # Hàng 1
        [ 2,  2,  0,-10, -8,-10,  0,  2,  2], # Hàng 2
        [ 0,  0, -2,  4, 10,  4, -2,  0,  0], # Hàng 3 (Ven sông địch)
        [ 0,  0,  2,  8,  2,  0,  0,  0,  0], # Hàng 4 (Sông)
        [-2,  0,  4,  2,  6,  2,  4,  0, -2], # Hàng 5 (Ven sông nhà)
        [ 0,  0,  0,  2,  4,  2,  0,  0,  0], # Hàng 6
        [ 4,  0,  8,  6, 10,  6,  8,  0,  4], # Hàng 7 (Thường đặt pháo tai sĩ)
        [ 0,  2,  4,  6,  6,  6,  4,  2,  0], # Hàng 8
        [ 0,  0,  2,  6,  6,  6,  2,  0,  0]  # Hàng 9: Đáy nhà
    ]

    CHARIOT_PST = [
        [14, 14, 12, 18, 16, 18, 12, 14, 14], # Hàng 0: Đáy địch
        [16, 20, 18, 24, 26, 24, 18, 20, 16], # Hàng 1
        [12, 12, 12, 18, 18, 18, 12, 12, 12], # Hàng 2
        [12, 18, 16, 22, 22, 22, 16, 18, 12], # Hàng 3 (Tuần hà địch / Cửu cung)
        [12, 14, 12, 18, 18, 18, 12, 14, 12], # Hàng 4 (Qua sông)
        [12, 16, 14, 20, 20, 20, 14, 16, 12], # Hàng 5 (Tuần hà nhà)
        [ 6, 10,  8, 14, 14, 14,  8, 10,  6], # Hàng 6
        [ 4,  8,  6, 14, 12, 14,  6,  8,  4], # Hàng 7
        [ 8,  4,  8, 16,  8, 16,  8,  4,  8], # Hàng 8 (Xe kẹt nếu chưa xuất)
        [-2, 10,  6, 14, 12, 14,  6, 10, -2]  # Hàng 9 (Đáy nhà)
    ]

    def __init__(self, board):
        """
        Args:
            board (Board): Instance bàn cờ
        """
        self.board = board
        self.current_score = self._calculate_initial_score()
        
    def _calculate_initial_score(self):
        score = 0
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                score += self.get_piece_score(self.board.get_piece(row, col), row, col)
        return score
        
    def get_piece_score(self, piece, row, col):
        """Tính điểm của một quân cờ tại một vị trí cụ thể"""
        if piece == Board.EMPTY:
            return 0
            
        piece_value = self.get_piece_value(piece)
        is_red = piece > 0
        abs_piece = abs(piece)
        eval_row = row if is_red else 9 - row
        position_bonus = 0
        
        if abs_piece == Board.RED_PAWN:
            position_bonus = self.PAWN_PST[eval_row][col]
        elif abs_piece == Board.RED_HORSE:
            position_bonus = self.HORSE_PST[eval_row][col]
        elif abs_piece == Board.RED_CANNON:
            position_bonus = self.CANNON_PST[eval_row][col]
        elif abs_piece == Board.RED_CHARIOT:
            position_bonus = self.CHARIOT_PST[eval_row][col]
            
        final_value = piece_value + position_bonus
        return final_value if is_red else -final_value
        
    def update_move(self, from_row, from_col, to_row, to_col, piece, captured_piece):
        """Cập nhật điểm tĩnh khi thực hiện một nước đi (O(1))"""
        # Bỏ điểm của quân cờ ở vị trí cũ
        self.current_score -= self.get_piece_score(piece, from_row, from_col)
        
        # Nếu có ăn quân, bỏ điểm của quân bị ăn
        if captured_piece != Board.EMPTY:
            self.current_score -= self.get_piece_score(captured_piece, to_row, to_col)
            
        # Thêm điểm của quân cờ ở vị trí mới
        self.current_score += self.get_piece_score(piece, to_row, to_col)
        
    def undo_update_move(self, from_row, from_col, to_row, to_col, piece, captured_piece):
        """Hoàn tác điểm tĩnh khi undo một nước đi (O(1))"""
        # Bỏ điểm của quân cờ ở vị trí mới
        self.current_score -= self.get_piece_score(piece, to_row, to_col)
        
        # Thêm lại điểm của quân bị ăn (nếu có)
        if captured_piece != Board.EMPTY:
            self.current_score += self.get_piece_score(captured_piece, to_row, to_col)
            
        # Thêm lại điểm của quân cờ ở vị trí cũ
        self.current_score += self.get_piece_score(piece, from_row, from_col)
    
    def evaluate(self):
        """
        Đánh giá trạng thái hiện tại của bàn cờ (O(1))
        
        Return:
            int: Điểm số (dương = Đỏ tốt, âm = Đen tốt)
        """
        return self.current_score
    
    def get_piece_value(self, piece):
        """
        Lấy giá trị của một quân (giá trị tuyệt đối)
        
        Args:
            piece (int): Mã quân
        
        Return:
            int: Giá trị của quân (0 nếu ô trống)
        """
        if piece == Board.EMPTY:
            return 0
        
        return self.PIECE_VALUES.get(piece, 0)


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    evaluator = Evaluator(board)
    score = evaluator.evaluate()
    print(f"Điểm số ban đầu: {score}")