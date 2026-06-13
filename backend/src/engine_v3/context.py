"""Shared one-dimensional position operations for the V3 search."""

import time
from dataclasses import dataclass

from src.board import Board
from src.engine_v3.evaluation import EvaluatorV3
from src.engine_v3.move import coordinates, source_square, target_square
from src.engine_v3.position import PositionUndo, PositionV3
from src.engine_v3.zobrist import ZobristHasher


Move = int


class SearchTimeout(Exception):
    """Raised to discard an incomplete iterative-deepening iteration."""


@dataclass
class UndoState:
    position_undo: PositionUndo
    synced_board: bool


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

    @property
    def zobrist_key(self):
        return self.position.zobrist_key

    @property
    def repetition_counts(self):
        return self.position.repetition_counts

    @property
    def king_positions(self):
        return {
            side: None if index is None else coordinates(index)
            for side, index in self.position.king_squares.items()
        }

    def start(self):
        self.start_time = time.perf_counter()
        self.evaluator._calculate_initial_score()
        self.position = PositionV3(self.board, self.zobrist)
        self.evaluation_cache.clear()
        self.fast_evaluation_cache.clear()

    def check_time(self):
        if time.perf_counter() - self.start_time > self.time_limit:
            raise SearchTimeout

    def pseudo_moves(self, is_red_turn, captures_only=False):
        return self.position.generate_moves(is_red_turn, captures_only)

    def legal_moves(self, is_red_turn, captures_only=False):
        moves = []
        for move in self.pseudo_moves(is_red_turn, captures_only):
            undo = self.position.make_move(move, is_red_turn)
            if undo is not None:
                moves.append(move)
                self.position.unmake_move(undo)
        return moves

    def has_legal_move(self, is_red_turn):
        for move in self.pseudo_moves(is_red_turn):
            undo = self.position.make_move(move, is_red_turn)
            if undo is not None:
                self.position.unmake_move(undo)
                return True
        return False

    def is_capture(self, move):
        return self.position.squares[target_square(move)] != Board.EMPTY

    def piece_at_source(self, move):
        return self.position.squares[source_square(move)]

    def move_target(self, move):
        return coordinates(target_square(move))

    def push(self, move, is_red_turn=None, sync_board=False):
        piece = self.position.squares[source_square(move)]
        moving_side = piece > 0 if is_red_turn is None else is_red_turn
        position_undo = self.position.make_move(move, moving_side)
        if position_undo is None:
            return None

        from_row, from_col = coordinates(source_square(move))
        to_row, to_col = coordinates(target_square(move))
        self.evaluator.update_move(
            from_row,
            from_col,
            to_row,
            to_col,
            position_undo.piece,
            position_undo.captured_piece,
        )
        if sync_board:
            self.board.board[to_row][to_col] = position_undo.piece
            self.board.board[from_row][from_col] = Board.EMPTY
            self.board.half_move_clock = self.position.half_move_clock
        return UndoState(position_undo, sync_board)

    def pop(self, undo):
        position_undo = undo.position_undo
        from_row, from_col = coordinates(source_square(position_undo.move))
        to_row, to_col = coordinates(target_square(position_undo.move))
        self.position.unmake_move(position_undo)
        if undo.synced_board:
            self.board.board[from_row][from_col] = position_undo.piece
            self.board.board[to_row][to_col] = position_undo.captured_piece
            self.board.half_move_clock = position_undo.old_clock
        self.evaluator.undo_update_move(
            from_row,
            from_col,
            to_row,
            to_col,
            position_undo.piece,
            position_undo.captured_piece,
        )

    def evaluate_for_side(self, is_red_turn, dynamic=False):
        cache = self.evaluation_cache if dynamic else self.fast_evaluation_cache
        score = cache.get(self.zobrist_key)
        if score is None:
            score = self.evaluator.evaluate() if dynamic else self.evaluator.evaluate_fast()
            if len(cache) >= 65_536:
                cache.clear()
            cache[self.zobrist_key] = score
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
            or self.repetition_counts[self.zobrist_key] >= 3
        )

    def state_key(self, is_red_turn):
        return self.zobrist.position_key(self.zobrist_key, is_red_turn)

    def has_non_pawn_material(self, is_red_turn):
        return any(
            piece != Board.EMPTY
            and (piece > 0) == is_red_turn
            and abs(piece) not in (Board.RED_KING, Board.RED_PAWN)
            for piece in self.position.squares
        )
