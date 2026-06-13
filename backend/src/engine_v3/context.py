"""Shared board operations for the V3 search."""

import time
from dataclasses import dataclass

from src.board import Board
from src.engine_v3.evaluation import EvaluatorV3
from src.engine_v3.zobrist import ZobristHasher
from src.move_gen import MoveGenerator


Move = tuple[int, int, int, int]


class SearchTimeout(Exception):
    """Raised to discard an incomplete iterative-deepening iteration."""


@dataclass
class UndoState:
    move: Move
    piece: int
    captured_piece: int
    old_clock: int
    old_zobrist_key: int


class SearchContext:
    def __init__(self, board, time_limit):
        self.board = board
        self.time_limit = time_limit
        self.move_gen = MoveGenerator(board)
        self.evaluator = EvaluatorV3(board)
        self.zobrist = ZobristHasher()
        self.zobrist_key = 0
        self.evaluation_cache = {}
        self.start_time = 0.0

    def start(self):
        self.start_time = time.perf_counter()
        self.evaluator._calculate_initial_score()
        self.zobrist_key = self.zobrist.hash_board(self.board)
        self.evaluation_cache.clear()

    def check_time(self):
        if time.perf_counter() - self.start_time > self.time_limit:
            raise SearchTimeout

    def legal_moves(self, is_red_turn):
        moves = []
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if piece == Board.EMPTY or (piece > 0) != is_red_turn:
                    continue

                for to_row, to_col in self.move_gen.generate_moves(row, col):
                    move = (row, col, to_row, to_col)
                    if not self.board.would_repeat_threefold(*move):
                        moves.append(move)
        return moves

    def is_capture(self, move):
        return self.board.get_piece(move[2], move[3]) != Board.EMPTY

    def push(self, move):
        from_row, from_col, to_row, to_col = move
        piece = self.board.get_piece(from_row, from_col)
        captured_piece = self.board.get_piece(to_row, to_col)
        undo = UndoState(
            move,
            piece,
            captured_piece,
            self.board.half_move_clock,
            self.zobrist_key,
        )

        self.evaluator.update_move(
            from_row,
            from_col,
            to_row,
            to_col,
            piece,
            captured_piece,
        )
        self.zobrist_key = self.zobrist.update_move(
            self.zobrist_key,
            move,
            piece,
            captured_piece,
        )
        self.board.move_piece(from_row, from_col, to_row, to_col)
        return undo

    def pop(self, undo):
        from_row, from_col, to_row, to_col = undo.move
        self.board.undo_move(
            from_row,
            from_col,
            to_row,
            to_col,
            undo.piece,
            undo.captured_piece,
            undo.old_clock,
        )
        self.evaluator.undo_update_move(
            from_row,
            from_col,
            to_row,
            to_col,
            undo.piece,
            undo.captured_piece,
        )
        self.zobrist_key = undo.old_zobrist_key

    def evaluate_for_side(self, is_red_turn):
        score = self.evaluation_cache.get(self.zobrist_key)
        if score is None:
            score = self.evaluator.evaluate()
            if len(self.evaluation_cache) >= 65_536:
                self.evaluation_cache.clear()
            self.evaluation_cache[self.zobrist_key] = score
        return score if is_red_turn else -score

    def is_in_check(self, is_red_turn):
        color = "red" if is_red_turn else "black"
        return self.move_gen.is_king_in_check(color)

    def game_result_for_side(self, is_red_turn):
        result = self.board.is_game_over()
        if result is None:
            return None
        current_side_won = result == ("red_win" if is_red_turn else "black_win")
        return 1 if current_side_won else -1

    def is_draw(self):
        if self.board.half_move_clock >= 120:
            return True
        state_hash = self.board.get_state_hash()
        return self.board.history.count(state_hash) >= 3

    def state_key(self, is_red_turn):
        return self.zobrist.position_key(self.zobrist_key, is_red_turn)

    def has_non_pawn_material(self, is_red_turn):
        for row in range(self.board.BOARD_ROWS):
            for col in range(self.board.BOARD_COLS):
                piece = self.board.get_piece(row, col)
                if (
                    piece != Board.EMPTY
                    and (piece > 0) == is_red_turn
                    and abs(piece) not in (Board.RED_KING, Board.RED_PAWN)
                ):
                    return True
        return False
