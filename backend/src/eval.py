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

    def __init__(self, board):
        """
        Args:
            board (Board): Instance bàn cờ
        """
        self.board = board
    
    def evaluate(self):
        """
        Đánh giá trạng thái hiện tại của bàn cờ
        
        Return:
            int: Điểm số (dương = Đỏ tốt, âm = Đen tốt)
        """
        score = 0
        
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                
                if piece == Board.EMPTY:
                    continue
                
                # Lấy giá trị quân
                piece_value = self.get_piece_value(piece)
                
                # Tính trọng số vị trí (Heuristic kiểm soát trung tâm)
                is_red = piece > 0
                abs_piece = abs(piece)
                eval_row = row if is_red else 9 - row  # Lật ngược hàng nếu là cờ Đen
                position_bonus = 0
                
                if abs_piece == Board.RED_PAWN:
                    position_bonus = self.PAWN_PST[eval_row][col]
                elif abs_piece == Board.RED_HORSE:
                    position_bonus = self.HORSE_PST[eval_row][col]
                
                final_value = piece_value + position_bonus
                
                # Cộng/trừ điểm
                if is_red:
                    score += final_value
                else:
                    score -= final_value
        
        return score
    
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