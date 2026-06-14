"""
eval.py - Hàm đánh giá thế cờ (Evaluation function) với Tapered Evaluation
"""

from core.board import Board


class Evaluator:
    """Lớp đánh giá thế cờ"""
    
    # Điểm số của từng loại quân (Khai/Trung cuộc)
    MG_PIECE_VALUES = {
        Board.RED_KING: 6000, Board.BLACK_KING: 6000,
        Board.RED_CHARIOT: 600, Board.BLACK_CHARIOT: 600,
        Board.RED_HORSE: 270, Board.BLACK_HORSE: 270,
        Board.RED_ELEPHANT: 120, Board.BLACK_ELEPHANT: 120,
        Board.RED_CANNON: 285, Board.BLACK_CANNON: 285,
        Board.RED_ADVISOR: 120, Board.BLACK_ADVISOR: 120,
        Board.RED_PAWN: 30, Board.BLACK_PAWN: 30,
    }

    # Điểm số của từng loại quân (Tàn cuộc)
    EG_PIECE_VALUES = {
        Board.RED_KING: 6000, Board.BLACK_KING: 6000,
        Board.RED_CHARIOT: 600, Board.BLACK_CHARIOT: 600,
        Board.RED_HORSE: 300, Board.BLACK_HORSE: 300,    # Mã mạnh hơn ở tàn cuộc
        Board.RED_ELEPHANT: 120, Board.BLACK_ELEPHANT: 120,
        Board.RED_CANNON: 250, Board.BLACK_CANNON: 250,  # Pháo yếu hơn ở tàn cuộc do thiếu ngòi
        Board.RED_ADVISOR: 120, Board.BLACK_ADVISOR: 120,
        Board.RED_PAWN: 50, Board.BLACK_PAWN: 50,      # Tốt mạnh hơn khi áp sát
    }

    # Trọng số tính Phase (tối đa 16)
    PHASE_WEIGHTS = {
        Board.RED_CHARIOT: 2, Board.BLACK_CHARIOT: 2,
        Board.RED_HORSE: 1,   Board.BLACK_HORSE: 1,
        Board.RED_CANNON: 1,  Board.BLACK_CANNON: 1,
    }

    # ================= PST CHO KHAI/TRUNG CUỘC (MG) =================
    MG_KING_PST = [
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0, -50, -50, -50,   0,   0,   0], # Lầu 3: Dễ bị tấn công
        [  0,   0,   0, -40, -40, -40,   0,   0,   0], # Lầu 2
        [  0,   0,   0,  10,  20,  10,   0,   0,   0], # Lầu 1 (Đáy): An toàn nhất
    ]

    MG_PAWN_PST = [
        [  0,   3,   6,   9,  12,   9,   6,   3,   0],
        [ 18,  36,  56,  80, 120,  80,  56,  36,  18],
        [ 14,  26,  42,  60,  80,  60,  42,  26,  14],
        [ 10,  20,  30,  34,  40,  34,  30,  20,  10],
        [  6,  12,  18,  18,  20,  18,  18,  12,   6],
        [  2,   0,   8,   0,   8,   0,   8,   0,   2],
        [  0,   0,  -2,   0,   4,   0,  -2,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
    ]

    MG_HORSE_PST = [
        [  4,   8,  16,  12,   4,  12,  16,   8,   4],
        [  4,  10,  28,  16,   8,  16,  28,  10,   4],
        [ 12,  14,  16,  20,  18,  20,  16,  14,  12],
        [  8,  24,  18,  24,  20,  24,  18,  24,   8],
        [  6,  16,  14,  18,  16,  18,  14,  16,   6],
        [  4,  12,  16,  14,  12,  14,  16,  12,   4],
        [  2,   6,   8,   6,  10,   6,   8,   6,   2],
        [  4,   2,   8,   8,   4,   8,   8,   2,   4],
        [  0,   2,   4,   4,  -2,   4,   4,   2,   0],
        [  0,  -4,   0,   0,   0,   0,   0,  -4,   0],
    ]

    MG_CANNON_PST = [
        [  6,   4,   0, -10, -12, -10,   0,   4,   6],
        [  2,   2,   0,  -4, -14,  -4,   0,   2,   2],
        [  2,   2,   0, -10,  -8, -10,   0,   2,   2],
        [  0,   0,  -2,   4,  10,   4,  -2,   0,   0],
        [  0,   0,   2,   8,   2,   0,   0,   0,   0],
        [ -2,   0,   4,   2,   6,   2,   4,   0,  -2],
        [  0,   0,   0,   2,   4,   2,   0,   0,   0],
        [  4,   0,   8,   6,  10,   6,   8,   0,   4],
        [  0,   2,   4,   6,   6,   6,   4,   2,   0],
        [  0,   0,   2,   6,   6,   6,   2,   0,   0],
    ]

    MG_CHARIOT_PST = [
        [ 14,  14,  12,  18,  16,  18,  12,  14,  14],
        [ 16,  20,  18,  24,  26,  24,  18,  20,  16],
        [ 12,  12,  12,  18,  18,  18,  12,  12,  12],
        [ 12,  18,  16,  22,  22,  22,  16,  18,  12],
        [ 12,  14,  12,  18,  18,  18,  12,  14,  12],
        [ 12,  16,  14,  20,  20,  20,  14,  16,  12],
        [  6,  10,   8,  14,  14,  14,   8,  10,   6],
        [  4,   8,   6,  14,  12,  14,   6,   8,   4],
        [  8,   4,   8,  16,   8,  16,   8,   4,   8],
        [ -2,  10,   6,  14,  12,  14,   6,  10,  -2],
    ]

    # ================= PST CHO TÀN CUỘC (EG) =================
    EG_KING_PST = [
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,   0,   0,   0,   0,   0,   0],
        [  0,   0,   0,  30,  20,  30,   0,   0,   0], # Lầu 3: Trợ công mạnh (lộ mặt)
        [  0,   0,   0,  20,  20,  20,   0,   0,   0], # Lầu 2
        [  0,   0,   0,  30,  20,  30,   0,   0,   0], # Lầu 1: Tù túng
    ]

    EG_PAWN_PST = [
        [  0,   6,  12,  18,  24,  18,  12,   6,   0], # Tốt tàn đe dọa cao
        [  0,   8,  16,  24,  32,  24,  16,   8,   0],
        [  0,   8,  16,  24,  32,  24,  16,   8,   0],
        [  0,   4,   8,  12,  16,  12,   8,   4,   0],
        [  0,   2,   4,   6,   8,   6,   4,   2,   0],
        [ -2,   0,   0,   0,   0,   0,   0,   0,  -2],
        [ -2,   0,   0,   0,   0,   0,   0,   0,  -2],
        [ -2,   0,   0,   0,   0,   0,   0,   0,  -2],
        [ -2,   0,   0,   0,   0,   0,   0,   0,  -2],
        [ -2,   0,   0,   0,   0,   0,   0,   0,  -2],
    ]

    # Ở tàn cuộc, Mã và Xe ưu tiên ở các vị trí tấn công và trung tâm tương tự MG nhưng trọng số có thể thay đổi
    # Để giữ code ngắn gọn và hiệu quả, ta có thể dùng chung PST MG cho Mã, Pháo, Xe
    EG_HORSE_PST = MG_HORSE_PST
    EG_CANNON_PST = MG_CANNON_PST
    EG_CHARIOT_PST = MG_CHARIOT_PST

    def __init__(self, board):
        """
        Args:
            board (Board): Instance bàn cờ
        """
        self.board = board
        self.mg_score = 0
        self.eg_score = 0
        self.phase = 0
        self._calculate_initial_score()
        
    def _calculate_initial_score(self):
        """Tính điểm và phase ban đầu bằng cách quét cả bàn cờ"""
        self.mg_score = 0
        self.eg_score = 0
        self.phase = 0
        
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece != Board.EMPTY:
                    mg, eg = self.get_piece_score(piece, row, col)
                    self.mg_score += mg
                    self.eg_score += eg
                    
                    if abs(piece) in self.PHASE_WEIGHTS:
                        self.phase += self.PHASE_WEIGHTS[abs(piece)]
                        
    def get_piece_score(self, piece, row, col):
        """
        Tính điểm MG và EG của một quân cờ tại một vị trí cụ thể
        Return: (mg_score, eg_score)
        """
        if piece == Board.EMPTY:
            return 0, 0
            
        abs_piece = abs(piece)
        is_red = piece > 0
        eval_row = row if is_red else 9 - row
        
        mg_val = self.MG_PIECE_VALUES.get(abs_piece, 0)
        eg_val = self.EG_PIECE_VALUES.get(abs_piece, 0)
        
        mg_bonus = 0
        eg_bonus = 0
        
        if abs_piece == Board.RED_PAWN:
            mg_bonus = self.MG_PAWN_PST[eval_row][col]
            eg_bonus = self.EG_PAWN_PST[eval_row][col]
        elif abs_piece == Board.RED_HORSE:
            mg_bonus = self.MG_HORSE_PST[eval_row][col]
            eg_bonus = self.EG_HORSE_PST[eval_row][col]
        elif abs_piece == Board.RED_CANNON:
            mg_bonus = self.MG_CANNON_PST[eval_row][col]
            eg_bonus = self.EG_CANNON_PST[eval_row][col]
        elif abs_piece == Board.RED_CHARIOT:
            mg_bonus = self.MG_CHARIOT_PST[eval_row][col]
            eg_bonus = self.EG_CHARIOT_PST[eval_row][col]
        elif abs_piece == Board.RED_KING:
            mg_bonus = self.MG_KING_PST[eval_row][col]
            eg_bonus = self.EG_KING_PST[eval_row][col]
            
        final_mg = mg_val + mg_bonus
        final_eg = eg_val + eg_bonus
        
        if is_red:
            return final_mg, final_eg
        else:
            return -final_mg, -final_eg
            
    def update_move(self, from_row, from_col, to_row, to_col, piece, captured_piece):
        """Cập nhật điểm tĩnh khi thực hiện một nước đi (O(1))"""
        # Bỏ điểm của quân cờ ở vị trí cũ
        mg_old, eg_old = self.get_piece_score(piece, from_row, from_col)
        self.mg_score -= mg_old
        self.eg_score -= eg_old
        
        # Nếu có ăn quân, bỏ điểm của quân bị ăn và giảm Phase
        if captured_piece != Board.EMPTY:
            mg_cap, eg_cap = self.get_piece_score(captured_piece, to_row, to_col)
            self.mg_score -= mg_cap
            self.eg_score -= eg_cap
            if abs(captured_piece) in self.PHASE_WEIGHTS:
                self.phase -= self.PHASE_WEIGHTS[abs(captured_piece)]
            
        # Thêm điểm của quân cờ ở vị trí mới
        mg_new, eg_new = self.get_piece_score(piece, to_row, to_col)
        self.mg_score += mg_new
        self.eg_score += eg_new
        
    def undo_update_move(self, from_row, from_col, to_row, to_col, piece, captured_piece):
        """Hoàn tác điểm tĩnh khi undo một nước đi (O(1))"""
        # Bỏ điểm của quân cờ ở vị trí mới
        mg_new, eg_new = self.get_piece_score(piece, to_row, to_col)
        self.mg_score -= mg_new
        self.eg_score -= eg_new
        
        # Thêm lại điểm của quân bị ăn (nếu có) và khôi phục Phase
        if captured_piece != Board.EMPTY:
            mg_cap, eg_cap = self.get_piece_score(captured_piece, to_row, to_col)
            self.mg_score += mg_cap
            self.eg_score += eg_cap
            if abs(captured_piece) in self.PHASE_WEIGHTS:
                self.phase += self.PHASE_WEIGHTS[abs(captured_piece)]
            
        # Thêm lại điểm của quân cờ ở vị trí cũ
        mg_old, eg_old = self.get_piece_score(piece, from_row, from_col)
        self.mg_score += mg_old
        self.eg_score += eg_old
    
    def evaluate(self):
        """
        Đánh giá trạng thái hiện tại của bàn cờ (O(1)) kết hợp nội suy Khai - Tàn cuộc
        
        Return:
            int: Điểm số (dương = Đỏ tốt, âm = Đen tốt)
        """
        # Đảm bảo phase nằm trong khoảng [0, 16]
        phase_p = max(0, min(16, self.phase))
        
        # Nội suy tuyến tính (Linear Interpolation)
        # Khi phase_p = 16 (Full Khai cuộc), kết quả hoàn toàn là mg_score
        # Khi phase_p = 0 (Tàn cuộc hoàn toàn), kết quả hoàn toàn là eg_score
        return (self.mg_score * phase_p + self.eg_score * (16 - phase_p)) // 16
        
    def get_piece_value(self, piece):
        """Hàm cũ giữ lại để tương thích với _score_move trong ai_engine"""
        if piece == Board.EMPTY:
            return 0
        return self.MG_PIECE_VALUES.get(abs(piece), 0)


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    evaluator = Evaluator(board)
    score = evaluator.evaluate()
    print(f"Điểm số ban đầu: {score}")
    print(f"MG Score: {evaluator.mg_score}, EG Score: {evaluator.eg_score}, Phase: {evaluator.phase}")
