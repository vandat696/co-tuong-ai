"""One-dimensional Xiangqi position for the V3 search."""

import json
from collections import Counter
from dataclasses import dataclass

from src.board import Board
from src.engine_v3.move import (
    coordinates,
    encode_move,
    source_square,
    square,
    target_square,
)


ORTHOGONALS = ((0, 1), (0, -1), (1, 0), (-1, 0))
DIAGONALS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
HORSE_MOVES = (
    (1, 2), (1, -2), (-1, 2), (-1, -2),
    (2, 1), (2, -1), (-2, 1), (-2, -1),
)


@dataclass
class PositionUndo:
    move: int
    piece: int
    captured_piece: int
    old_clock: int
    old_zobrist_key: int
    old_red_king: int | None
    old_black_king: int | None


class PositionV3:
    """Search-only position with flat board and incremental state."""

    def __init__(self, board, zobrist):
        self.zobrist = zobrist
        self.squares = [piece for row in board.board for piece in row]
        self.half_move_clock = board.half_move_clock
        self.king_squares = {
            True: self._find_piece(Board.RED_KING),
            False: self._find_piece(Board.BLACK_KING),
        }
        self.zobrist_key = self.zobrist.hash_squares(self.squares)
        self.repetition_counts = Counter(
            self.zobrist.hash_squares([piece for row in json.loads(state) for piece in row])
            for state in board.history
        )

    def _find_piece(self, wanted):
        try:
            return self.squares.index(wanted)
        except ValueError:
            return None

    @staticmethod
    def _valid(row, col):
        return 0 <= row < 10 and 0 <= col < 9

    @staticmethod
    def _in_palace(row, col, is_red):
        return 3 <= col <= 5 and ((7 <= row <= 9) if is_red else (0 <= row <= 2))

    def generate_moves(self, is_red_turn, captures_only=False):
        moves = []
        for source, piece in enumerate(self.squares):
            if piece == Board.EMPTY or (piece > 0) != is_red_turn:
                continue
            for target in self._piece_targets(source, piece):
                if captures_only and self.squares[target] == Board.EMPTY:
                    continue
                moves.append(encode_move(source, target))
        return moves

    def _piece_targets(self, source, piece):
        row, col = coordinates(source)
        kind = abs(piece)
        if kind == Board.RED_KING:
            return self._step_targets(row, col, piece, ORTHOGONALS, palace=True)
        if kind == Board.RED_ADVISOR:
            return self._step_targets(row, col, piece, DIAGONALS, palace=True)
        if kind == Board.RED_ELEPHANT:
            return self._elephant_targets(row, col, piece)
        if kind == Board.RED_CHARIOT:
            return self._sliding_targets(row, col, piece, cannon=False)
        if kind == Board.RED_HORSE:
            return self._horse_targets(row, col, piece)
        if kind == Board.RED_CANNON:
            return self._sliding_targets(row, col, piece, cannon=True)
        if kind == Board.RED_PAWN:
            return self._pawn_targets(row, col, piece)
        return []

    def _step_targets(self, row, col, piece, offsets, palace=False):
        targets = []
        for dr, dc in offsets:
            to_row, to_col = row + dr, col + dc
            if not self._valid(to_row, to_col):
                continue
            if palace and not self._in_palace(to_row, to_col, piece > 0):
                continue
            target = square(to_row, to_col)
            if self.squares[target] == Board.EMPTY or self.squares[target] * piece < 0:
                targets.append(target)
        return targets

    def _elephant_targets(self, row, col, piece):
        targets = []
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            to_row, to_col = row + dr, col + dc
            if not self._valid(to_row, to_col):
                continue
            if (piece > 0 and to_row < 5) or (piece < 0 and to_row > 4):
                continue
            if self.squares[square(row + dr // 2, col + dc // 2)] != Board.EMPTY:
                continue
            target = square(to_row, to_col)
            if self.squares[target] == Board.EMPTY or self.squares[target] * piece < 0:
                targets.append(target)
        return targets

    def _horse_targets(self, row, col, piece):
        targets = []
        for dr, dc in HORSE_MOVES:
            to_row, to_col = row + dr, col + dc
            if not self._valid(to_row, to_col):
                continue
            leg = square(row + (1 if dr > 0 else -1), col) if abs(dr) == 2 else square(row, col + (1 if dc > 0 else -1))
            target = square(to_row, to_col)
            if self.squares[leg] == Board.EMPTY and (
                self.squares[target] == Board.EMPTY or self.squares[target] * piece < 0
            ):
                targets.append(target)
        return targets

    def _sliding_targets(self, row, col, piece, cannon):
        targets = []
        for dr, dc in ORTHOGONALS:
            to_row, to_col = row + dr, col + dc
            screened = False
            while self._valid(to_row, to_col):
                target = square(to_row, to_col)
                occupant = self.squares[target]
                if not cannon:
                    if occupant == Board.EMPTY:
                        targets.append(target)
                    else:
                        if occupant * piece < 0:
                            targets.append(target)
                        break
                elif not screened:
                    if occupant == Board.EMPTY:
                        targets.append(target)
                    else:
                        screened = True
                elif occupant != Board.EMPTY:
                    if occupant * piece < 0:
                        targets.append(target)
                    break
                to_row += dr
                to_col += dc
        return targets

    def _pawn_targets(self, row, col, piece):
        forward = -1 if piece > 0 else 1
        offsets = [(forward, 0)]
        if (piece > 0 and row <= 4) or (piece < 0 and row >= 5):
            offsets.extend(((0, 1), (0, -1)))
        return self._step_targets(row, col, piece, offsets)

    def make_move(self, move, is_red_turn):
        source = source_square(move)
        target = target_square(move)
        piece = self.squares[source]
        captured = self.squares[target]
        undo = PositionUndo(
            move,
            piece,
            captured,
            self.half_move_clock,
            self.zobrist_key,
            self.king_squares[True],
            self.king_squares[False],
        )

        self.squares[target] = piece
        self.squares[source] = Board.EMPTY
        if abs(piece) == Board.RED_KING:
            self.king_squares[is_red_turn] = target
        if abs(captured) == Board.RED_KING:
            self.king_squares[captured > 0] = None
        self.zobrist_key = self.zobrist.update_indices(
            self.zobrist_key, source, target, piece, captured
        )
        self.half_move_clock = 0 if captured or abs(piece) == Board.RED_PAWN else self.half_move_clock + 1
        self.repetition_counts[self.zobrist_key] += 1

        if self.is_in_check(is_red_turn) or self.repetition_counts[self.zobrist_key] >= 3:
            self.unmake_move(undo)
            return None
        return undo

    def unmake_move(self, undo):
        self.repetition_counts[self.zobrist_key] -= 1
        if self.repetition_counts[self.zobrist_key] <= 0:
            del self.repetition_counts[self.zobrist_key]
        source = source_square(undo.move)
        target = target_square(undo.move)
        self.squares[source] = undo.piece
        self.squares[target] = undo.captured_piece
        self.half_move_clock = undo.old_clock
        self.zobrist_key = undo.old_zobrist_key
        self.king_squares[True] = undo.old_red_king
        self.king_squares[False] = undo.old_black_king

    def is_in_check(self, is_red_turn):
        king = self.king_squares[is_red_turn]
        return king is None or self.is_square_attacked(king, not is_red_turn)

    def is_square_attacked(self, target, by_red):
        row, col = coordinates(target)
        sign = 1 if by_red else -1
        for dr, dc in ORTHOGONALS:
            scan_row, scan_col = row + dr, col + dc
            blockers = 0
            while self._valid(scan_row, scan_col):
                piece = self.squares[square(scan_row, scan_col)]
                if piece:
                    blockers += 1
                    if blockers == 1 and piece in (sign * Board.RED_CHARIOT, sign * Board.RED_KING):
                        return True
                    if blockers == 2:
                        if piece == sign * Board.RED_CANNON:
                            return True
                        break
                scan_row += dr
                scan_col += dc

        for dr, dc in HORSE_MOVES:
            source_row, source_col = row - dr, col - dc
            if not self._valid(source_row, source_col):
                continue
            if self.squares[square(source_row, source_col)] != sign * Board.RED_HORSE:
                continue
            leg = square(source_row + (1 if dr > 0 else -1), source_col) if abs(dr) == 2 else square(source_row, source_col + (1 if dc > 0 else -1))
            if self.squares[leg] == Board.EMPTY:
                return True

        pawn_row = row + (1 if by_red else -1)
        if self._valid(pawn_row, col) and self.squares[square(pawn_row, col)] == sign * Board.RED_PAWN:
            return True
        crossed = row <= 4 if by_red else row >= 5
        if crossed:
            for pawn_col in (col - 1, col + 1):
                if self._valid(row, pawn_col) and self.squares[square(row, pawn_col)] == sign * Board.RED_PAWN:
                    return True
        return False
