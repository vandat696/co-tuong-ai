"""
ai_engine.py - Minimax engine cho cờ tướng
"""

import time
from src.board import Board
from src.move_gen import MoveGenerator
from src.eval import Evaluator


class AIEngine:
    """Lớp AI engine dùng Minimax"""
    
    def __init__(self, board, max_depth=4, time_limit=2.0):
        """
        Args:
            board (Board): Instance bàn cờ
            max_depth (int): Độ sâu tìm kiếm tối đa
            time_limit (float): Giới hạn thời gian suy nghĩ (giây)
        """
        self.board = board
        self.max_depth = max_depth
        self.time_limit = time_limit
        self.start_time = 0
        self.timeout = False
        self.move_gen = MoveGenerator(board)
        self.evaluator = Evaluator(board)
    
    def get_best_move(self, is_red_turn):
        """
        Tìm nước đi tốt nhất với Iterative Deepening (Tính giờ)
        """
        self.start_time = time.time()
        self.timeout = False
        best_move_overall = None
        
        # Đào sâu lặp dần từ depth 1 đến max_depth
        for depth in range(1, self.max_depth + 1):
            move = self._search_root(depth, is_red_turn)
            
            if self.timeout:
                break  # Hết giờ, dừng việc tìm kiếm sâu hơn
                
            if move is not None:
                best_move_overall = move  # Cập nhật nước đi tốt nhất của độ sâu này
                
        return best_move_overall

    def _search_root(self, depth, is_red_turn):
        """
        Khởi chạy tìm kiếm Minimax tại gốc cho một độ sâu cụ thể
        
        Args:
            depth (int): Độ sâu ở vòng lặp hiện tại
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
        alpha = -float('inf')
        beta = float('inf')
        
        if is_red_turn:
            best_score = -float('inf')
            for from_row, from_col, to_row, to_col in all_moves:
                # Lưu quân bị bắt
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                # Di chuyển
                self.board.move_piece(from_row, from_col, to_row, to_col)
                
                # Gọi minimax có alpha, beta
                score = self.minimax(depth - 1, False, alpha, beta)
                
                # Undo di chuyển
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                # Nếu hết giờ khi đang ở giữa nhánh, hủy bỏ kết quả không trọn vẹn này
                if self.timeout:
                    return None

                if score > best_score:
                    best_score = score
                    best_move = (from_row, from_col, to_row, to_col)
                alpha = max(alpha, best_score)
        else:
            best_score = float('inf')
            for from_row, from_col, to_row, to_col in all_moves:
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                self.board.move_piece(from_row, from_col, to_row, to_col)
                score = self.minimax(depth - 1, True, alpha, beta)
                
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                if self.timeout:
                    return None

                if score < best_score:
                    best_score = score
                    best_move = (from_row, from_col, to_row, to_col)
                beta = min(beta, best_score)
        
        return best_move
    
    def minimax(self, depth, is_red_maximizing, alpha=-float('inf'), beta=float('inf')):
        """
        Thuật toán Minimax
        
        Args:
            depth (int): Độ sâu hiện tại (0 = đánh giá)
            is_red_maximizing (bool): True = AI Đỏ (muốn MAX), False = AI Đen (muốn MIN)
            alpha (float): Giá trị tốt nhất cờ Đỏ (MAX) có thể đảm bảo
            beta (float): Giá trị tốt nhất cờ Đen (MIN) có thể đảm bảo
        
        Return:
            int: Điểm số tốt nhất
        """
        # ===== Kiểm tra thời gian =====
        if time.time() - self.start_time > self.time_limit:
            self.timeout = True
            return 0
            
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
                score = self.minimax(depth - 1, False, alpha, beta)
                
                # Undo
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                # Cập nhật
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                
                # Tỉa nhánh (Pruning)
                if beta <= alpha:
                    break
            
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
                score = self.minimax(depth - 1, True, alpha, beta)
                
                # Undo
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                # Cập nhật
                min_score = min(min_score, score)
                beta = min(beta, score)
                
                # Tỉa nhánh (Pruning)
                if beta <= alpha:
                    break
            
            return min_score


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    engine = AIEngine(board, max_depth=2)
    
    # AI Đỏ tính nước đi
    move = engine.get_best_move(is_red_turn=True)
    print(f"Nước đi tốt nhất của Đỏ: {move}")