"""
board.py - Biểu diễn bàn cờ tướng 10x9 và xử lý trạng thái cơ bản
"""

class Board:
    """Lớp đại diện cho bàn cờ tướng"""
    
    # Hằng số định nghĩa quân cờ
    EMPTY = 0
    
    # Quân Đỏ (dương)
    RED_KING = 1
    RED_ADVISOR = 2
    RED_ELEPHANT = 3
    RED_CHARIOT = 4
    RED_HORSE = 5
    RED_CANNON = 6
    RED_PAWN = 7
    
    # Quân Đen (âm)
    BLACK_KING = -1
    BLACK_ADVISOR = -2
    BLACK_ELEPHANT = -3
    BLACK_CHARIOT = -4
    BLACK_HORSE = -5
    BLACK_CANNON = -6
    BLACK_PAWN = -7
    
    # Kích thước bàn
    BOARD_ROWS = 10
    BOARD_COLS = 9
    
    def __init__(self):
        """Khởi tạo bàn cờ ở trạng thái ban đầu"""
        self.board = self._init_board()
        self.current_player = 'red'  # Đỏ đi trước
    
    def _init_board(self):
        """
        Khởi tạo bàn cờ ở trạng thái ban đầu
        
        Return:
            list: Mảng 10x9 biểu diễn bàn cờ
        """
        # TODO: Tạo mảng 10x9, điền các quân vào vị trí ban đầu
        # Gợi ý: Sử dụng [[EMPTY] * 9 for _ in range(10)] để tạo mảng trống
        # Rồi điền các hàng 0, 1, 2 cho quân Đỏ
        #       và hàng 7, 8, 9 cho quân Đen
        board = [[self.EMPTY] * 9 for _ in range(10)]
        # ====== QUÂN ĐỎ =======
        board[0] = [self.RED_CHARIOT, self.RED_HORSE, self.RED_ELEPHANT, self.RED_ADVISOR,
                    self.RED_KING,
                    self.RED_ADVISOR, self.RED_ELEPHANT, self.RED_HORSE, self.RED_CHARIOT]
        board[2][1] = self.RED_CANNON
        board[2][7] = self.RED_CANNON
        for col in range(0, 9, 2):
            board[3][col] = self.RED_PAWN
        # ====== QUÂN ĐEN =======
        board[9] = [self.BLACK_CHARIOT, self.BLACK_HORSE, self.BLACK_ELEPHANT, self.BLACK_ADVISOR,
                    self.BLACK_KING,
                    self.BLACK_ADVISOR, self.BLACK_ELEPHANT, self.BLACK_HORSE, self.BLACK_CHARIOT]
        board[7][1] = self.BLACK_CANNON
        board[7][7] = self.BLACK_CANNON
        for col in range(0, 9, 2):
            board[6][col] = self.BLACK_PAWN
        return board
    
    def get_piece(self, row, col):
        """
        Lấy quân tại vị trí (row, col)
        
        Args:
            row (int): Hàng (0-9)
            col (int): Cột (0-8)
        
        Return:
            int: Mã quân (hoặc 0 nếu ô trống)
        """
        if self._is_valid_pos(row, col):
            return self.board[row][col]
        return None
    
    def set_piece(self, row, col, piece):
        """
        Đặt quân tại vị trí (row, col)
        
        Args:
            row (int): Hàng
            col (int): Cột
            piece (int): Mã quân
        """
        if self._is_valid_pos(row, col):
            self.board[row][col] = piece
    
    def _is_valid_pos(self, row, col):
        """
        Kiểm tra vị trí có hợp lệ không
        
        Args:
            row (int): Hàng
            col (int): Cột
        
        Return:
            bool: True nếu hợp lệ, False nếu không
        """
        return 0 <= row < self.BOARD_ROWS and 0 <= col < self.BOARD_COLS
    
    def is_red(self, piece):
        """Kiểm tra quân có phải Đỏ không (số dương)"""
        return piece > 0
    
    def is_black(self, piece):
        """Kiểm tra quân có phải Đen không (số âm)"""
        return piece < 0
    
    def move_piece(self, from_row, from_col, to_row, to_col):
        """
        Di chuyển quân từ (from_row, from_col) đến (to_row, to_col)
        
        Args:
            from_row, from_col: Vị trí quân hiện tại
            to_row, to_col: Vị trí mới
        
        Return:
            bool: True nếu di chuyển thành công, False nếu không hợp lệ
        """
        # TODO: Kiểm tra cả hai vị trí có hợp lệ không, rồi di chuyển
        # Cấu trúc: 
        #   1. Kiểm tra from_row, from_col hợp lệ
        if not (0 <= from_row < 10 and 0 <= from_col < 9):
            return False
        #   2. Kiểm tra to_row, to_col hợp lệ
        if not (0 <= to_row < 10 and 0 <= to_col < 9):
            return False
        #   3. Lấy quân từ vị trí cũ
        piece = self.board[from_row][from_col]
        if piece == self.EMPTY:
            return False
        #   4. Đặt quân vào vị trí mới
        self.board[to_row][to_col] = piece        
        #   5. Đặt EMPTY tại vị trí cũ
        self.board[from_row][from_col] = self.EMPTY
        #   6. Return True
        return True
    
    def find_king(self, color):
        """
        Tìm vị trí Tướng của một bên
        
        Args:
            color (str): 'red' hoặc 'black'
        
        Return:
            tuple: (row, col) hoặc None nếu không tìm thấy
        """
        # TODO: Duyệt qua toàn bộ bàn cờ, tìm Tướng
        if color == "red":
            king = self.RED_KING
        else:
            king = self.BLACK_KING
        for row in range(10):
            for col in range(9):
                if self.board[row][col] == king:
                    return (row, col)
        return None
        # Gợi ý: Dùng RED_KING, BLACK_KING để tìm
    
    def is_game_over(self):
        """
        Kiểm tra game có kết thúc không (một bên mất Tướng)
        
        Return:
            str: 'red_win', 'black_win', hoặc None nếu game chưa kết thúc
        """
        # TODO: Kiểm tra xem Tướng nào bị mất
        red_king = self.find_king("red")
        black_king = self.find_king("black")
        # Nếu Tướng Đỏ mất → Đen thắng
        if red_king is None:
            return "black_win"
        # Nếu Tướng Đen mất → Đỏ thắng
        if black_king is None:
            return "red_win"
        # Nếu cả hai có → Game chưa kết thúc
        return None
    
    def print_board(self):
        """In bàn cờ ra màn hình (cho debug)"""
        print("    0 1 2 3 4 5 6 7 8")
        for row in range(self.BOARD_ROWS):
            print(f"{row}: ", end="")
            for col in range(self.BOARD_COLS):
                piece = self.get_piece(row, col)
                print(f"{piece:2d} ", end="")
            print()
        print()


# Test đơn giản
if __name__ == "__main__":
    board = Board()
    board.print_board()