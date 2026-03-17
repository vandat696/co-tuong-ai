"""
eval.py - Hàm đánh giá thế cờ (Evaluation function)
"""

from src.board import Board


class Evaluator:
    """Lớp đánh giá thế cờ"""
    
    # Điểm số của từng loại quân
    PIECE_VALUES = {
        Board.RED_KING: 1000,
        Board.RED_CHARIOT: 20,
        Board.RED_HORSE: 9,
        Board.RED_ELEPHANT: 5,
        Board.RED_CANNON: 10,
        Board.RED_ADVISOR: 4,
        Board.RED_PAWN: 2,
        
        Board.BLACK_KING: 1000,
        Board.BLACK_CHARIOT: 20,
        Board.BLACK_HORSE: 9,
        Board.BLACK_ELEPHANT: 5,
        Board.BLACK_CANNON: 10,
        Board.BLACK_ADVISOR: 4,
        Board.BLACK_PAWN: 2,
    }
    
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
                
                # Kiểm tra Tốt: chưa qua sông vs đã qua sông
                if abs(piece) == Board.RED_PAWN or abs(piece) == Board.BLACK_PAWN:
                    if piece > 0:  # Tốt Đỏ
                        # Đỏ: row >= 5 → đã qua sông
                        if row >= 5:
                            piece_value = 4  # Tốt đã qua sông
                        else:
                            piece_value = 2  # Tốt chưa qua sông
                    else:  # Tốt Đen
                        # Đen: row <= 4 → đã qua sông
                        if row <= 4:
                            piece_value = 4  # Tốt đã qua sông
                        else:
                            piece_value = 2  # Tốt chưa qua sông
                
                # Cộng/trừ điểm
                if piece > 0:
                    score += piece_value
                else:
                    score -= piece_value
        
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