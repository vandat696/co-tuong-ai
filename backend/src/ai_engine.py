"""
ai_engine.py - Minimax engine cho cờ tướng
"""

from src.board import Board
from src.move_gen import MoveGenerator
from src.eval import Evaluator


class AIEngine:
    """Lớp AI engine dùng Minimax"""
    
    def __init__(self, board, max_depth=2):
        """
        Args:
            board (Board): Instance bàn cờ
            max_depth (int): Độ sâu tìm kiếm
        """
        self.board = board
        self.max_depth = max_depth
        self.move_gen = MoveGenerator(board)
        self.evaluator = Evaluator(board)
    
    def get_best_move(self, is_red_turn):
        """
        Tìm nước đi tốt nhất bằng Minimax
        
        Args:
            is_red_turn (bool): True nếu là lượt Đỏ, False là lượt Đen
        
        Return:
            tuple: (best_row, best_col) hoặc None nếu không có nước đi
        """
        # Sinh tất cả nước đi hợp lệ
        all_moves = []
        
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                
                # Kiểm tra quân của mình
                if piece == Board.EMPTY:
                    continue
                
                is_red_piece = piece > 0
                if is_red_piece != is_red_turn:
                    continue
                
                # Sinh nước đi cho quân này
                moves = self.move_gen.generate_moves(row, col)
                for to_row, to_col in moves:
                    all_moves.append((row, col, to_row, to_col))
        
        # Nếu không có nước đi
        if not all_moves:
            return None
        
        # Tìm nước đi tốt nhất
        best_move = None
        best_score = -float('inf') if is_red_turn else float('inf')
        
        for from_row, from_col, to_row, to_col in all_moves:
            # Lưu quân bị bắt
            piece = self.board.get_piece(from_row, from_col)
            captured_piece = self.board.get_piece(to_row, to_col)
            
            # Di chuyển
            self.board.move_piece(from_row, from_col, to_row, to_col)
            
            # Gọi minimax
            score = self.minimax(self.max_depth - 1, not is_red_turn)
            
            # Undo di chuyển
            self.board.set_piece(from_row, from_col, piece)
            self.board.set_piece(to_row, to_col, captured_piece)
            
            # Cập nhật nước tốt nhất
            if is_red_turn:
                if score > best_score:
                    best_score = score
                    best_move = (from_row, from_col, to_row, to_col)
            else:
                if score < best_score:
                    best_score = score
                    best_move = (from_row, from_col, to_row, to_col)
        
        return best_move
    
    def minimax(self, depth, is_red_maximizing):
        """
        Thuật toán Minimax
        
        Args:
            depth (int): Độ sâu hiện tại (0 = đánh giá)
            is_red_maximizing (bool): True = AI Đỏ (muốn MAX), False = AI Đen (muốn MIN)
        
        Return:
            int: Điểm số tốt nhất
        """
        # ===== Cơ sở đệ quy =====
        if depth == 0:
            return self.evaluator.evaluate()
        
        # Kiểm tra game đã kết thúc
        game_result = self.board.is_game_over()
        if game_result == "red_win":
            return 10000  # Đỏ thắng
        elif game_result == "black_win":
            return -10000  # Đen thắng
        
        # ===== Sinh nước đi =====
        all_moves = []
        
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                
                if piece == Board.EMPTY:
                    continue
                
                # Kiểm tra quân của bên hiện tại
                is_red_piece = piece > 0
                if is_red_piece != is_red_maximizing:
                    continue
                
                # Sinh nước đi
                moves = self.move_gen.generate_moves(row, col)
                for to_row, to_col in moves:
                    all_moves.append((row, col, to_row, to_col))
        
        # Nếu không có nước đi
        if not all_moves:
            return self.evaluator.evaluate()
        
        # ===== Minimax logic =====
        if is_red_maximizing:
            # MAX: Đỏ muốn điểm cao
            max_score = -float('inf')
            
            for from_row, from_col, to_row, to_col in all_moves:
                # Lưu quân
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                # Di chuyển
                self.board.move_piece(from_row, from_col, to_row, to_col)
                
                # Đệ quy
                score = self.minimax(depth - 1, False)
                
                # Undo
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                # Cập nhật
                max_score = max(max_score, score)
            
            return max_score
        else:
            # MIN: Đen muốn điểm thấp
            min_score = float('inf')
            
            for from_row, from_col, to_row, to_col in all_moves:
                # Lưu quân
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                # Di chuyển
                self.board.move_piece(from_row, from_col, to_row, to_col)
                
                # Đệ quy
                score = self.minimax(depth - 1, True)
                
                # Undo
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                # Cập nhật
                min_score = min(min_score, score)
            
            return min_score


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    engine = AIEngine(board, max_depth=2)
    
    # AI Đỏ tính nước đi
    move = engine.get_best_move(is_red_turn=True)
    print(f"Nước đi tốt nhất của Đỏ: {move}")