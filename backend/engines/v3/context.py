"""Shared one-dimensional position operations for the V3 search."""

import time

from core.board import Board
from engines.v3.evaluation import EvaluatorV3
from engines.v3.move import coordinates, source_square, target_square
from engines.v3.position import PositionV3
from engines.v3.zobrist import ZobristHasher


Move = int


class SearchTimeout(Exception):
    """Raised to discard an incomplete iterative-deepening iteration."""


class SearchContext:
    def __init__(self, board, time_limit):
        self.board = board
        self.time_limit = time_limit
        self.evaluator = EvaluatorV3(board)
        self.zobrist = ZobristHasher()
        self.position = None
        self.evaluation_cache = {}
        self.fast_evaluation_cache = {}
        self.start_time = 0.0
        self.deadline = 0.0
        self.time_check_countdown = 256

    @property
    def zobrist_key(self):
        return self.position.zobrist_key

    @property
    def repetition_counts(self):
        return self.position.repetition_keys

    @property
    def king_positions(self):
        return {
            side: None if index is None else coordinates(index)
            for side, index in self.position.king_squares.items()
        }

    def start(self):
        self.start_time = time.perf_counter()
        self.deadline = self.start_time + self.time_limit
        self.time_check_countdown = 256
        self.evaluator._calculate_initial_score()
        self.position = PositionV3(self.board, self.zobrist)
        self.evaluation_cache.clear()
        self.fast_evaluation_cache.clear()

    def check_time(self, force=False):
        self.time_check_countdown -= 1
        if not force and self.time_check_countdown > 0:
            return
        self.time_check_countdown = 256
        if time.perf_counter() > self.deadline:
            raise SearchTimeout

    def pseudo_moves(self, is_red_turn, captures_only=False):
        return self.position.generate_moves(is_red_turn, captures_only)

    def legal_moves(self, is_red_turn, captures_only=False):
        moves = []
        for move in self.pseudo_moves(is_red_turn, captures_only):
            if self.position.make_move(move, is_red_turn):
                moves.append(move)
                self.position.unmake_move()
        return moves

    def has_legal_move(self, is_red_turn):
        for move in self.pseudo_moves(is_red_turn):
            if self.position.make_move(move, is_red_turn):
                self.position.unmake_move()
                return True
        return False

    def is_capture(self, move):
        return self.position.squares[target_square(move)] != Board.EMPTY

    def captured_piece(self, move):
        return self.position.squares[target_square(move)]

    def piece_at_source(self, move):
        return self.position.squares[source_square(move)]

    def move_target(self, move):
        return coordinates(target_square(move))

    def push(self, move, is_red_turn=None):
        piece = self.position.squares[source_square(move)]
        moving_side = piece > 0 if is_red_turn is None else is_red_turn
        return True if self.position.make_move(move, moving_side) else None

    def pop(self, undo):
        self.position.unmake_move()

    def evaluate_for_side(self, is_red_turn, dynamic=False):
        if not dynamic:
            score = self.position.evaluate()
            return score if is_red_turn else -score
        score = self.evaluation_cache.get(self.zobrist_key)
        if score is None:
            score = self.evaluator.evaluate()
            if len(self.evaluation_cache) >= 65_536:
                self.evaluation_cache.clear()
            self.evaluation_cache[self.zobrist_key] = score
        return score if is_red_turn else -score

    def is_in_check(self, is_red_turn):
        return self.position.is_in_check(is_red_turn)

    def is_square_attacked(self, row, col, by_red):
        return self.position.is_square_attacked(row * 9 + col, by_red)

    def game_result_for_side(self, is_red_turn):
        if self.position.king_squares[is_red_turn] is None:
            return -1
        if self.position.king_squares[not is_red_turn] is None:
            return 1
        return None

    def is_draw(self):
        return (
            self.position.half_move_clock >= 120
            or self.position.repetition_keys.count(self.zobrist_key) >= 3
        )

    def state_key(self, is_red_turn):
        return self.zobrist.position_key(self.zobrist_key, is_red_turn)

    def has_non_pawn_material(self, is_red_turn):
        return any(
            abs(self.position.squares[source])
            not in (Board.RED_KING, Board.RED_PAWN)
            for source in self.position.piece_lists[1 if is_red_turn else 0]
        )
