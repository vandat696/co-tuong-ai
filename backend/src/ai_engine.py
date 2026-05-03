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
        self.transposition_table = {}  # Bộ nhớ đệm Transposition Table
        self.move_gen = MoveGenerator(board)
        self.evaluator = Evaluator(board)
    
    def get_best_move(self, is_red_turn):
        """
        Tìm nước đi tốt nhất với Iterative Deepening (Tính giờ)
        """
        self.start_time = time.time()
        self.timeout = False
        self.transposition_table.clear()  # Xóa cache mỗi lượt mới để tránh tràn RAM
        best_move_overall = None
        
        # Đào sâu lặp dần từ depth 1 đến max_depth
        for depth in range(1, self.max_depth + 1):
            move = self._search_root(depth, is_red_turn, best_move_overall)
            
            if self.timeout:
                break  # Hết giờ, dừng việc tìm kiếm sâu hơn
                
            if move is not None:
                best_move_overall = move  # Cập nhật nước đi tốt nhất của độ sâu này
                
        return best_move_overall

    def _search_root(self, depth, is_red_turn, tt_best_move=None):
        """
        Khởi chạy tìm kiếm Minimax tại gốc cho một độ sâu cụ thể
        
        Args:
            depth (int): Độ sâu ở vòng lặp hiện tại
            is_red_turn (bool): True nếu là lượt Đỏ, False là lượt Đen
            tt_best_move (tuple): Nước đi tốt nhất từ độ sâu trước
        
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
            
        # Sắp xếp nước đi ưu tiên (Move Ordering)
        all_moves.sort(key=lambda m: self._score_move(m, tt_best_move), reverse=True)
        
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

    def _score_move(self, move, tt_move):
        """
        Đánh giá điểm sơ bộ của một nước đi để SẮP XẾP ƯU TIÊN (Move Ordering).
        MVV-LVA: Most Valuable Victim - Least Valuable Attacker
        """
        if move == tt_move:
            return 1000000  # Ưu tiên tuyệt đối nước đi tốt nhất từ Cache (TT Move)
            
        from_row, from_col, to_row, to_col = move
        captured_piece = self.board.get_piece(to_row, to_col)
        
        if captured_piece != Board.EMPTY:
            attacker = self.board.get_piece(from_row, from_col)
            # Ưu tiên ăn quân to của địch bằng quân nhỏ của mình
            return 10 * self.evaluator.get_piece_value(captured_piece) - self.evaluator.get_piece_value(attacker)
            
        return 0  # Nước đi thường

    def quiescence_search(self, alpha, beta, is_red_maximizing):
        """
        Tìm kiếm tĩnh (Quiescence Search) để tránh Horizon Effect.
        Chỉ duyệt các nước ĂN QUÂN cho đến khi trạng thái bớt biến động.
        """
        # 1. Kiểm tra hết giờ
        if time.time() - self.start_time > self.time_limit:
            self.timeout = True
            return 0
            
        # 2. Stand Pat (Đánh giá tĩnh hiện tại)
        # Giả định cơ bản: Người chơi luôn có thể chọn "không làm gì cả" nếu các nước ăn quân đều tệ.
        stand_pat = self.evaluator.evaluate()
        
        if is_red_maximizing:
            if stand_pat >= beta:
                return beta  # Fail-high (Cắt tỉa)
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha # Fail-low (Cắt tỉa)
            beta = min(beta, stand_pat)
            
        # 3. Chỉ sinh ra các nước ĂN QUÂN
        capture_moves = []
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece == Board.EMPTY:
                    continue
                
                is_red_piece = piece > 0
                if is_red_piece != is_red_maximizing:
                    continue
                    
                moves = self.move_gen.generate_moves(row, col)
                for to_row, to_col in moves:
                    # Nếu ô đích có quân -> Đây là nước ăn quân
                    if self.board.get_piece(to_row, to_col) != Board.EMPTY:
                        capture_moves.append((row, col, to_row, to_col))
                        
        # Nếu không có nước ăn quân nào, trả về điểm Stand Pat
        if not capture_moves:
            return stand_pat
            
        # Sắp xếp các nước ăn quân (MVV-LVA) để tối ưu cắt tỉa
        capture_moves.sort(key=lambda m: self._score_move(m, None), reverse=True)
        
        # 4. Đệ quy QSearch
        if is_red_maximizing:
            for from_row, from_col, to_row, to_col in capture_moves:
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                self.board.move_piece(from_row, from_col, to_row, to_col)
                score = self.quiescence_search(alpha, beta, False)
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                if score >= beta:
                    return beta
                alpha = max(alpha, score)
            return alpha
        else:
            for from_row, from_col, to_row, to_col in capture_moves:
                piece = self.board.get_piece(from_row, from_col)
                captured_piece = self.board.get_piece(to_row, to_col)
                
                self.board.move_piece(from_row, from_col, to_row, to_col)
                score = self.quiescence_search(alpha, beta, True)
                self.board.set_piece(from_row, from_col, piece)
                self.board.set_piece(to_row, to_col, captured_piece)
                
                if score <= alpha:
                    return alpha
                beta = min(beta, score)
            return beta
    
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
            
        # ===== Tra cứu Transposition Table (Cache) =====
        # Dùng chuỗi string của ma trận bàn cờ làm Khóa (Key)
        state_key = (str(self.board.board), is_red_maximizing)
        tt_entry = self.transposition_table.get(state_key)
        tt_best_move = None
        
        if tt_entry is not None and tt_entry['depth'] >= depth:
            tt_flag = tt_entry['flag']
            tt_score = tt_entry['score']
            
            if tt_flag == 'EXACT':
                return tt_score
            elif tt_flag == 'LOWERBOUND':
                alpha = max(alpha, tt_score)
            elif tt_flag == 'UPPERBOUND':
                beta = min(beta, tt_score)
                
            if alpha >= beta:
                return tt_score
                
        # Lấy nước đi tốt nhất từ Cache để ưu tiên duyệt trước
        if tt_entry is not None and 'best_move' in tt_entry:
            tt_best_move = tt_entry['best_move']
                
        # Lưu lại alpha, beta ban đầu để quyết định cờ (flag) khi lưu Cache
        original_alpha = alpha
        original_beta = beta

        # ===== Cơ sở đệ quy =====
        if depth == 0:
            # Khi hết depth, thay vì evaluate ngay, ta chuyển sang QSearch để giải quyết các tranh chấp
            return self.quiescence_search(alpha, beta, is_red_maximizing)
        
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
            return self.quiescence_search(alpha, beta, is_red_maximizing)
        
        # Sắp xếp nước đi (Move Ordering) để tăng hiệu quả Alpha-Beta Pruning
        all_moves.sort(key=lambda m: self._score_move(m, tt_best_move), reverse=True)
        
        best_move_this_node = None
        
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
                if score > max_score:
                    max_score = score
                    best_move_this_node = (from_row, from_col, to_row, to_col)
                alpha = max(alpha, score)
                
                # Tỉa nhánh (Pruning)
                if beta <= alpha:
                    break
            
            # Ghi vào Cache trước khi return
            if not self.timeout:
                if max_score <= original_alpha:
                    flag = 'UPPERBOUND'
                elif max_score >= beta:
                    flag = 'LOWERBOUND'
                else:
                    flag = 'EXACT'
                self.transposition_table[state_key] = {
                    'depth': depth, 'score': max_score, 'flag': flag, 'best_move': best_move_this_node}
                
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
                if score < min_score:
                    min_score = score
                    best_move_this_node = (from_row, from_col, to_row, to_col)
                beta = min(beta, score)
                
                # Tỉa nhánh (Pruning)
                if beta <= alpha:
                    break
            
            # Ghi vào Cache trước khi return
            if not self.timeout:
                if min_score >= original_beta:
                    flag = 'LOWERBOUND'
                elif min_score <= alpha:
                    flag = 'UPPERBOUND'
                else:
                    flag = 'EXACT'
                self.transposition_table[state_key] = {
                    'depth': depth, 'score': min_score, 'flag': flag, 'best_move': best_move_this_node}
                
            return min_score


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    engine = AIEngine(board, max_depth=2)
    
    # AI Đỏ tính nước đi
    move = engine.get_best_move(is_red_turn=True)
    print(f"Nước đi tốt nhất của Đỏ: {move}")