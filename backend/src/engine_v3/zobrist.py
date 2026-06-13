"""Deterministic incremental Zobrist hashing for Xiangqi positions."""

import random


class ZobristHasher:
    def __init__(self, seed=0xC0_7A_0A):
        rng = random.Random(seed)
        self.piece_keys = {
            piece: [
                [rng.getrandbits(64) for _ in range(9)]
                for _ in range(10)
            ]
            for piece in range(-7, 8)
            if piece != 0
        }
        self.side_key = rng.getrandbits(64)

    def hash_board(self, board):
        return self.hash_matrix(board.board)

    def hash_matrix(self, matrix):
        key = 0
        for row, cells in enumerate(matrix):
            for col, piece in enumerate(cells):
                if piece:
                    key ^= self.piece_keys[piece][row][col]
        return key

    def hash_squares(self, squares):
        key = 0
        for index, piece in enumerate(squares):
            if piece:
                row, col = divmod(index, 9)
                key ^= self.piece_keys[piece][row][col]
        return key

    def update_indices(self, key, source, target, piece, captured_piece):
        from_row, from_col = divmod(source, 9)
        to_row, to_col = divmod(target, 9)
        key ^= self.piece_keys[piece][from_row][from_col]
        key ^= self.piece_keys[piece][to_row][to_col]
        if captured_piece:
            key ^= self.piece_keys[captured_piece][to_row][to_col]
        return key

    def update_move(self, key, move, piece, captured_piece):
        from_row, from_col, to_row, to_col = move
        key ^= self.piece_keys[piece][from_row][from_col]
        key ^= self.piece_keys[piece][to_row][to_col]
        if captured_piece:
            key ^= self.piece_keys[captured_piece][to_row][to_col]
        return key

    def position_key(self, board_key, is_red_turn):
        return board_key ^ (self.side_key if is_red_turn else 0)
