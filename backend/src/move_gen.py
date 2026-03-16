"""
move_gen.py - Sinh nước đi hợp lệ cho từng loại quân
"""

from board import Board


class MoveGenerator:
    """Lớp sinh nước đi hợp lệ"""
    
    def __init__(self, board):
        """Args:
            board (Board): Instance bàn cờ"""
        self.board = board
    
    # ============= HÀM CHÍNH =============
    
    def generate_moves(self, row, col):
        """
        Sinh tất cả nước đi hợp lệ cho quân tại (row, col)
        Args:
            row, col: Vị trí quân
        Return:
            list: Danh sách nước đi [(to_row, to_col), ...]
        """
        piece = self.board.get_piece(row, col)
        
        if piece == Board.EMPTY:
            return []
        
        abs_piece = abs(piece)
        
        # Gọi hàm tương ứng với loại quân
        if abs_piece == 1:  # King
            return self._get_king_moves(row, col, piece)
        elif abs_piece == 2:  # Advisor
            return self._get_advisor_moves(row, col, piece)
        elif abs_piece == 3:  # Elephant
            return self._get_elephant_moves(row, col, piece)
        elif abs_piece == 4:  # Chariot
            return self._get_chariot_moves(row, col, piece)
        elif abs_piece == 5:  # Horse
            return self._get_horse_moves(row, col, piece)
        elif abs_piece == 6:  # Cannon
            return self._get_cannon_moves(row, col, piece)
        elif abs_piece == 7:  # Pawn
            return self._get_pawn_moves(row, col, piece)
        
        return []
    
    # ============= HELPER FUNCTIONS =============
    
    def _is_in_palace(self, row, col, is_red):
        """
        Kiểm tra vị trí có nằm trong cung tướng không
        Cung Đỏ: hàng 0-2, cột 3-5
        Cung Đen: hàng 7-9, cột 3-5
        
        Args:
            row, col: Vị trí cần kiểm tra
            is_red: True nếu kiểm tra cung Đỏ, False là cung Đen
        
        Return:
            bool: True nếu nằm trong cung
        """
        if is_red:
            return 0 <= row <= 2 and 3 <= col <= 5
        else:
            return 7 <= row <= 9 and 3 <= col <= 5
    
    def _is_river(self, row):
        """
        Kiểm tra hàng có nằm ở sông không
        Sông nằm giữa hàng 4 và 5
        Args:
            row: Hàng cần kiểm tra
        Return:
            bool: True nếu nằm ở sông
        """
        return row == 4 or row == 5
    
    def _is_enemy(self, piece1, piece2):
        """
        Kiểm tra 2 quân có phải địch nhau không
        
        Args:
            piece1 (int): Quân 1
            piece2 (int): Quân 2
        
        Return:
            bool: True nếu chúng là kẻ thù
        """
        return piece1 * piece2 < 0
    
    def _is_blocked(self, from_row, from_col, to_row, to_col):
        """
        Kiểm tra đường đi từ from → to có bị chặn không
        (Dùng cho Xe, Pháo)
        
        Args:
            from_row, from_col: Vị trí gốc
            to_row, to_col: Vị trí đích
        
        Return:
            bool: True nếu bị chặn
        """
        # Tìm hướng đi
        row_step = 0 if from_row == to_row else (1 if to_row > from_row else -1)
        col_step = 0 if from_col == to_col else (1 if to_col > from_col else -1)
        
        # Duyệt qua các ô giữa (không tính điểm đầu cuối)
        current_row = from_row + row_step
        current_col = from_col + col_step
        
        while (current_row, current_col) != (to_row, to_col):
            if self.board.get_piece(current_row, current_col) != Board.EMPTY:
                return True
            current_row += row_step
            current_col += col_step
        
        return False
    
    # ============= CÁC HÀM SINH NƯỚC ĐI =============
    
    def _get_king_moves(self, row, col, piece):
        """
        Tướng: Di chuyển 1 ô orthogonal (ngang/dọc), chỉ trong cung
        """
        moves = []
        is_red = piece > 0
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Phải, Trái, Dưới, Lên
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra hợp lệ
            if not self.board._is_valid_pos(new_row, new_col):
                continue
            
            # Kiểm tra nằm trong cung
            if not self._is_in_palace(new_row, new_col, is_red):
                continue
            
            target_piece = self.board.get_piece(new_row, new_col)
            
            # EMPTY hoặc kẻ thù
            if target_piece == Board.EMPTY or self._is_enemy(piece, target_piece):
                moves.append((new_row, new_col))
        
        return moves
    
    def _get_advisor_moves(self, row, col, piece):
        """
        Sĩ: Di chuyển 1 ô chéo, chỉ trong cung
        """
        moves = []
        is_red = piece > 0
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # 4 hướng chéo
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra hợp lệ
            if not self.board._is_valid_pos(new_row, new_col):
                continue
            
            # Kiểm tra nằm trong cung
            if not self._is_in_palace(new_row, new_col, is_red):
                continue
            
            target_piece = self.board.get_piece(new_row, new_col)
            
            # EMPTY hoặc kẻ thù
            if target_piece == Board.EMPTY or self._is_enemy(piece, target_piece):
                moves.append((new_row, new_col))
        
        return moves
    
    def _get_elephant_moves(self, row, col, piece):
        """
        Tượng: Di chuyển 2 ô chéo, không qua sông, không bị chặn
        Quân chặn nằm ở giữa (1 ô chéo)
        """
        moves = []
        is_red = piece > 0
        directions = [(2, 2), (2, -2), (-2, 2), (-2, -2)]  # 4 hướng chéo 2 ô
        block_offsets = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Quân chặn tương ứng
        
        for i, (dr, dc) in enumerate(directions):
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra hợp lệ
            if not self.board._is_valid_pos(new_row, new_col):
                continue
            
            # Kiểm tra không vượt sông
            if is_red and new_row > 4:
                continue
            if not is_red and new_row < 5:
                continue
            
            # Kiểm tra quân chặn
            block_row = row + block_offsets[i][0]
            block_col = col + block_offsets[i][1]
            if self.board.get_piece(block_row, block_col) != Board.EMPTY:
                continue
            
            target_piece = self.board.get_piece(new_row, new_col)
            
            # EMPTY hoặc kẻ thù
            if target_piece == Board.EMPTY or self._is_enemy(piece, target_piece):
                moves.append((new_row, new_col))
        
        return moves
    
    def _get_chariot_moves(self, row, col, piece):
        """
        Xe: Di chuyển nhiều ô orthogonal, bị chặn bởi quân
        """
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            while self.board._is_valid_pos(new_row, new_col):
                target_piece = self.board.get_piece(new_row, new_col)
                
                if target_piece == Board.EMPTY:
                    # Ô trống → có thể đi
                    moves.append((new_row, new_col))
                elif self._is_enemy(piece, target_piece):
                    # Kẻ thù → có thể bắt rồi dừng
                    moves.append((new_row, new_col))
                    break
                else:
                    # Quân mình → dừng
                    break
                
                new_row += dr
                new_col += dc
        
        return moves
    
    def _get_horse_moves(self, row, col, piece):
        """
        Mã: Di chuyển L-shape (1 ngang + 1 chéo), không nhảy qua vật cản
        8 hướng có thể: (+1,-2), (+1,+2), (-1,-2), (-1,+2), (+2,-1), (+2,+1), (-2,-1), (-2,+1)
        Quân chặn nằm ở (row + row_step, col) hoặc (row, col + col_step)
        """
        moves = []
        # Các nước đi L-shape (row_step, col_step)
        l_moves = [(1, 2), (1, -2), (-1, 2), (-1, -2), (2, 1), (2, -1), (-2, 1), (-2, -1)]
        # Quân chặn tương ứng
        blocks = [(1, 0), (1, 0), (-1, 0), (-1, 0), (0, 1), (0, 1), (0, -1), (0, -1)]
        
        for i, (dr, dc) in enumerate(l_moves):
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra hợp lệ
            if not self.board._is_valid_pos(new_row, new_col):
                continue
            
            # Kiểm tra quân chặn
            block_row = row + blocks[i][0]
            block_col = col + blocks[i][1]
            if self.board.get_piece(block_row, block_col) != Board.EMPTY:
                continue
            
            target_piece = self.board.get_piece(new_row, new_col)
            
            # EMPTY hoặc kẻ thù
            if target_piece == Board.EMPTY or self._is_enemy(piece, target_piece):
                moves.append((new_row, new_col))
        
        return moves
    
    def _get_cannon_moves(self, row, col, piece):
        """
        Pháo: 
        - Di chuyển như Xe (không có quân phía trước)
        - Bắt quân khi có 1 quân làm "pháo đài" ở giữa
        """
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            found_blocker = False
            
            while self.board._is_valid_pos(new_row, new_col):
                target_piece = self.board.get_piece(new_row, new_col)
                
                if target_piece == Board.EMPTY:
                    # Ô trống
                    if not found_blocker:
                        # Chưa gặp pháo đài → di chuyển như Xe
                        moves.append((new_row, new_col))
                else:
                    # Có quân
                    if not found_blocker:
                        # Chưa gặp pháo đài → đây là pháo đài
                        found_blocker = True
                    else:
                        # Đã gặp pháo đài
                        if self._is_enemy(piece, target_piece):
                            # Kẻ thù → có thể bắt
                            moves.append((new_row, new_col))
                        # Dừng lại
                        break
                
                new_row += dr
                new_col += dc
        
        return moves
    
    def _get_pawn_moves(self, row, col, piece):
        """
        Tốt:
        - Trước sông: 1 ô lên phía địch (Đỏ: dưới, Đen: lên)
        - Sau sông (qua sông): 1 ô theo 3 hướng (lên, xuống, ngang)
        """
        moves = []
        is_red = piece > 0
        
        if is_red:
            # Tốt Đỏ: nước đi hướng xuống (tăng row)
            if row < 5:
                # Chưa qua sông: chỉ đi xuống
                directions = [(1, 0)]
            else:
                # Qua sông: đi 3 hướng
                directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        else:
            # Tốt Đen: nước đi hướng lên (giảm row)
            if row > 4:
                # Chưa qua sông: chỉ đi lên
                directions = [(-1, 0)]
            else:
                # Qua sông: đi 3 hướng
                directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra hợp lệ
            if not self.board._is_valid_pos(new_row, new_col):
                continue
            
            target_piece = self.board.get_piece(new_row, new_col)
            
            # EMPTY hoặc kẻ thù
            if target_piece == Board.EMPTY or self._is_enemy(piece, target_piece):
                moves.append((new_row, new_col))
        
        return moves


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    board.print_board
    move_gen = MoveGenerator(board)
    # Test sinh nước đi cho Xe Đỏ ở (0, 0)
    moves = move_gen.generate_moves(0, 0)
    print(f"Nước đi của Xe Đỏ ở (0,0): {moves}")
    # Test sinh nước đi cho Mã Đỏ ở (0, 1)
    moves = move_gen.generate_moves(0, 1)
    print(f"Nước đi của Mã Đỏ ở (0,1): {moves}")