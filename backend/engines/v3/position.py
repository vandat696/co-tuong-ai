"""One-dimensional Xiangqi position for the V3 search."""

import json

from core.board import Board
from engines.v1.eval import Evaluator
from engines.v3.move import (
    encode_move,
    source_square,
    target_square,
)


ORTHOGONALS = ((0, 1), (0, -1), (1, 0), (-1, 0))
DIAGONALS = ((1, 1), (1, -1), (-1, 1), (-1, -1))
HORSE_MOVES = (
    (1, 2), (1, -2), (-1, 2), (-1, -2),
    (2, 1), (2, -1), (-2, 1), (-2, -1),
)


def _build_rays():
    rays = []
    for source in range(90):
        row, col = divmod(source, 9)
        square_rays = []
        for dr, dc in ORTHOGONALS:
            ray = []
            scan_row, scan_col = row + dr, col + dc
            while 0 <= scan_row < 10 and 0 <= scan_col < 9:
                ray.append(scan_row * 9 + scan_col)
                scan_row += dr
                scan_col += dc
            square_rays.append(tuple(ray))
        rays.append(tuple(square_rays))
    return tuple(rays)


def _build_horse_attackers():
    attackers = []
    for target in range(90):
        row, col = divmod(target, 9)
        entries = []
        for dr, dc in HORSE_MOVES:
            source_row, source_col = row - dr, col - dc
            if not (0 <= source_row < 10 and 0 <= source_col < 9):
                continue
            leg = (
                (source_row + (1 if dr > 0 else -1)) * 9 + source_col
                if abs(dr) == 2
                else source_row * 9 + source_col + (1 if dc > 0 else -1)
            )
            entries.append((source_row * 9 + source_col, leg))
        attackers.append(tuple(entries))
    return tuple(attackers)


def _build_pawn_attackers(by_red):
    sign = -1 if by_red else 1
    attackers = []
    for target in range(90):
        row, col = divmod(target, 9)
        entries = []
        source_row = row - sign
        if 0 <= source_row < 10:
            entries.append(source_row * 9 + col)
        if (by_red and row <= 4) or (not by_red and row >= 5):
            if col > 0:
                entries.append(row * 9 + col - 1)
            if col < 8:
                entries.append(row * 9 + col + 1)
        attackers.append(tuple(entries))
    return tuple(attackers)


def _build_step_targets(offsets, palace_side=None):
    targets = []
    for source in range(90):
        row, col = divmod(source, 9)
        entries = []
        for dr, dc in offsets:
            to_row, to_col = row + dr, col + dc
            if not (0 <= to_row < 10 and 0 <= to_col < 9):
                continue
            if palace_side is not None and not (
                3 <= to_col <= 5
                and (
                    7 <= to_row <= 9
                    if palace_side
                    else 0 <= to_row <= 2
                )
            ):
                continue
            entries.append(to_row * 9 + to_col)
        targets.append(tuple(entries))
    return tuple(targets)


def _build_elephant_targets(is_red):
    targets = []
    for source in range(90):
        row, col = divmod(source, 9)
        entries = []
        for dr, dc in ((2, 2), (2, -2), (-2, 2), (-2, -2)):
            to_row, to_col = row + dr, col + dc
            if not (0 <= to_row < 10 and 0 <= to_col < 9):
                continue
            if (is_red and to_row < 5) or (not is_red and to_row > 4):
                continue
            entries.append(
                (
                    to_row * 9 + to_col,
                    (row + dr // 2) * 9 + col + dc // 2,
                )
            )
        targets.append(tuple(entries))
    return tuple(targets)


def _build_horse_targets():
    targets = []
    for source in range(90):
        row, col = divmod(source, 9)
        entries = []
        for dr, dc in HORSE_MOVES:
            to_row, to_col = row + dr, col + dc
            if not (0 <= to_row < 10 and 0 <= to_col < 9):
                continue
            leg = (
                (row + (1 if dr > 0 else -1)) * 9 + col
                if abs(dr) == 2
                else row * 9 + col + (1 if dc > 0 else -1)
            )
            entries.append((to_row * 9 + to_col, leg))
        targets.append(tuple(entries))
    return tuple(targets)


def _build_pawn_targets(is_red):
    targets = []
    for source in range(90):
        row, col = divmod(source, 9)
        entries = [(row - 1 if is_red else row + 1, col)]
        if (is_red and row <= 4) or (not is_red and row >= 5):
            entries.extend(((row, col - 1), (row, col + 1)))
        targets.append(
            tuple(
                to_row * 9 + to_col
                for to_row, to_col in entries
                if 0 <= to_row < 10 and 0 <= to_col < 9
            )
        )
    return tuple(targets)


RAYS = _build_rays()
HORSE_ATTACKERS = _build_horse_attackers()
HORSE_TARGETS = _build_horse_targets()
KING_TARGETS = {
    True: _build_step_targets(ORTHOGONALS, True),
    False: _build_step_targets(ORTHOGONALS, False),
}
ADVISOR_TARGETS = {
    True: _build_step_targets(DIAGONALS, True),
    False: _build_step_targets(DIAGONALS, False),
}
ELEPHANT_TARGETS = {
    True: _build_elephant_targets(True),
    False: _build_elephant_targets(False),
}
PAWN_TARGETS = {
    True: _build_pawn_targets(True),
    False: _build_pawn_targets(False),
}
PAWN_ATTACKERS = {
    True: _build_pawn_attackers(True),
    False: _build_pawn_attackers(False),
}


MAX_UNDO_PLY = 256


def _build_evaluation_tables():
    mg = [[0] * 90 for _ in range(15)]
    eg = [[0] * 90 for _ in range(15)]
    for piece in range(-7, 8):
        if piece == 0:
            continue
        piece_index = piece + 7
        kind = abs(piece)
        for target in range(90):
            row, col = divmod(target, 9)
            eval_row = row if piece > 0 else 9 - row
            mg_bonus = eg_bonus = 0
            if kind == Board.RED_PAWN:
                mg_bonus = Evaluator.MG_PAWN_PST[eval_row][col]
                eg_bonus = Evaluator.EG_PAWN_PST[eval_row][col]
            elif kind == Board.RED_HORSE:
                mg_bonus = Evaluator.MG_HORSE_PST[eval_row][col]
                eg_bonus = Evaluator.EG_HORSE_PST[eval_row][col]
            elif kind == Board.RED_CANNON:
                mg_bonus = Evaluator.MG_CANNON_PST[eval_row][col]
                eg_bonus = Evaluator.EG_CANNON_PST[eval_row][col]
            elif kind == Board.RED_CHARIOT:
                mg_bonus = Evaluator.MG_CHARIOT_PST[eval_row][col]
                eg_bonus = Evaluator.EG_CHARIOT_PST[eval_row][col]
            elif kind == Board.RED_KING:
                mg_bonus = Evaluator.MG_KING_PST[eval_row][col]
                eg_bonus = Evaluator.EG_KING_PST[eval_row][col]
            sign = 1 if piece > 0 else -1
            mg[piece_index][target] = sign * (
                Evaluator.MG_PIECE_VALUES[kind] + mg_bonus
            )
            eg[piece_index][target] = sign * (
                Evaluator.EG_PIECE_VALUES[kind] + eg_bonus
            )
    return tuple(tuple(row) for row in mg), tuple(tuple(row) for row in eg)


MG_SCORES, EG_SCORES = _build_evaluation_tables()
PHASE_WEIGHTS = tuple(Evaluator.PHASE_WEIGHTS.get(kind, 0) for kind in range(8))


class PositionV3:
    """Search-only position with flat board and incremental state."""

    def __init__(self, board, zobrist):
        self.zobrist = zobrist
        self.squares = [piece for row in board.board for piece in row]
        self.piece_lists = [[], []]
        self.piece_slots = [-1] * 90
        self.mg_score = 0
        self.eg_score = 0
        self.phase = 0
        for source, piece in enumerate(self.squares):
            if not piece:
                continue
            side = 1 if piece > 0 else 0
            self.piece_slots[source] = len(self.piece_lists[side])
            self.piece_lists[side].append(source)
            self.mg_score += MG_SCORES[piece + 7][source]
            self.eg_score += EG_SCORES[piece + 7][source]
            self.phase += PHASE_WEIGHTS[abs(piece)]
        self.half_move_clock = board.half_move_clock
        self.king_squares = {
            True: self._find_piece(Board.RED_KING),
            False: self._find_piece(Board.BLACK_KING),
        }
        self.zobrist_key = self.zobrist.hash_squares(self.squares)
        self.repetition_keys = [
            self.zobrist.hash_squares([piece for row in json.loads(state) for piece in row])
            for state in board.history
        ]
        self.undo_move = [0] * MAX_UNDO_PLY
        self.undo_piece = [0] * MAX_UNDO_PLY
        self.undo_captured = [0] * MAX_UNDO_PLY
        self.undo_clock = [0] * MAX_UNDO_PLY
        self.undo_hash = [0] * MAX_UNDO_PLY
        self.undo_red_king = [0] * MAX_UNDO_PLY
        self.undo_black_king = [0] * MAX_UNDO_PLY
        self.undo_captured_slot = [0] * MAX_UNDO_PLY
        self.undo_swapped_square = [0] * MAX_UNDO_PLY
        self.undo_ply = 0

    def _find_piece(self, wanted):
        try:
            return self.squares.index(wanted)
        except ValueError:
            return None

    def generate_moves(self, is_red_turn, captures_only=False):
        moves = []
        for source in self.piece_lists[1 if is_red_turn else 0]:
            piece = self.squares[source]
            targets = (
                self._capture_targets(source, piece)
                if captures_only
                else self._piece_targets(source, piece)
            )
            for target in targets:
                moves.append(encode_move(source, target))
        return moves

    def _piece_targets(self, source, piece):
        kind = abs(piece)
        if kind == Board.RED_KING:
            return self._step_targets(piece, KING_TARGETS[piece > 0][source])
        if kind == Board.RED_ADVISOR:
            return self._step_targets(piece, ADVISOR_TARGETS[piece > 0][source])
        if kind == Board.RED_ELEPHANT:
            return self._elephant_targets(source, piece)
        if kind == Board.RED_CHARIOT:
            return self._sliding_targets(source, piece, cannon=False)
        if kind == Board.RED_HORSE:
            return self._horse_targets(source, piece)
        if kind == Board.RED_CANNON:
            return self._sliding_targets(source, piece, cannon=True)
        if kind == Board.RED_PAWN:
            return self._step_targets(piece, PAWN_TARGETS[piece > 0][source])
        return []

    def _capture_targets(self, source, piece):
        if abs(piece) in (Board.RED_CHARIOT, Board.RED_CANNON):
            return self._sliding_captures(
                source,
                piece,
                cannon=abs(piece) == Board.RED_CANNON,
            )
        return [
            target
            for target in self._piece_targets(source, piece)
            if self.squares[target] != Board.EMPTY
        ]

    def _step_targets(self, piece, geometry):
        targets = []
        for target in geometry:
            occupant = self.squares[target]
            if occupant == Board.EMPTY or occupant * piece < 0:
                targets.append(target)
        return targets

    def _elephant_targets(self, source, piece):
        targets = []
        for target, eye in ELEPHANT_TARGETS[piece > 0][source]:
            if self.squares[eye] != Board.EMPTY:
                continue
            occupant = self.squares[target]
            if occupant == Board.EMPTY or occupant * piece < 0:
                targets.append(target)
        return targets

    def _horse_targets(self, source, piece):
        targets = []
        for target, leg in HORSE_TARGETS[source]:
            occupant = self.squares[target]
            if self.squares[leg] == Board.EMPTY and (
                occupant == Board.EMPTY or occupant * piece < 0
            ):
                targets.append(target)
        return targets

    def _sliding_targets(self, source, piece, cannon):
        targets = []
        for ray in RAYS[source]:
            screened = False
            for target in ray:
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
        return targets

    def _sliding_captures(self, source, piece, cannon):
        targets = []
        for ray in RAYS[source]:
            screened = False
            for target in ray:
                occupant = self.squares[target]
                if occupant == Board.EMPTY:
                    continue
                if not cannon:
                    if occupant * piece < 0:
                        targets.append(target)
                    break
                if not screened:
                    screened = True
                else:
                    if occupant * piece < 0:
                        targets.append(target)
                    break
        return targets

    def make_move(self, move, is_red_turn):
        source = source_square(move)
        target = target_square(move)
        piece = self.squares[source]
        captured = self.squares[target]
        captured_slot = self.piece_slots[target] if captured else -1
        ply = self.undo_ply
        self.undo_move[ply] = move
        self.undo_piece[ply] = piece
        self.undo_captured[ply] = captured
        self.undo_clock[ply] = self.half_move_clock
        self.undo_hash[ply] = self.zobrist_key
        self.undo_red_king[ply] = self.king_squares[True] if self.king_squares[True] is not None else -1
        self.undo_black_king[ply] = self.king_squares[False] if self.king_squares[False] is not None else -1
        self.undo_captured_slot[ply] = -1
        self.undo_swapped_square[ply] = -1
        self.undo_ply += 1

        self.squares[target] = piece
        self.squares[source] = Board.EMPTY
        moving_side = 1 if piece > 0 else 0
        moving_slot = self.piece_slots[source]
        self.piece_lists[moving_side][moving_slot] = target
        self.piece_slots[target] = moving_slot
        self.piece_slots[source] = -1
        if captured:
            captured_side = 1 if captured > 0 else 0
            swapped_square = self.piece_lists[captured_side][-1]
            self.undo_captured_slot[ply] = captured_slot
            self.undo_swapped_square[ply] = swapped_square
            self.piece_lists[captured_side][captured_slot] = swapped_square
            self.piece_slots[swapped_square] = captured_slot
            self.piece_lists[captured_side].pop()
            self.piece_slots[target] = moving_slot
        self.mg_score += (
            MG_SCORES[piece + 7][target]
            - MG_SCORES[piece + 7][source]
            - MG_SCORES[captured + 7][target]
        )
        self.eg_score += (
            EG_SCORES[piece + 7][target]
            - EG_SCORES[piece + 7][source]
            - EG_SCORES[captured + 7][target]
        )
        if captured:
            self.phase -= PHASE_WEIGHTS[abs(captured)]
        if abs(piece) == Board.RED_KING:
            self.king_squares[is_red_turn] = target
        if abs(captured) == Board.RED_KING:
            self.king_squares[captured > 0] = None
        self.zobrist_key = self.zobrist.update_indices(
            self.zobrist_key, source, target, piece, captured
        )
        self.half_move_clock = 0 if captured or abs(piece) == Board.RED_PAWN else self.half_move_clock + 1
        self.repetition_keys.append(self.zobrist_key)

        if self.is_in_check(is_red_turn) or self.repetition_keys.count(self.zobrist_key) >= 3:
            self.unmake_move()
            return False
        return True

    def unmake_move(self):
        self.repetition_keys.pop()
        self.undo_ply -= 1
        ply = self.undo_ply
        move = self.undo_move[ply]
        piece = self.undo_piece[ply]
        captured = self.undo_captured[ply]
        source = source_square(move)
        target = target_square(move)
        moving_side = 1 if piece > 0 else 0
        moving_slot = self.piece_slots[target]
        self.piece_lists[moving_side][moving_slot] = source
        self.piece_slots[source] = moving_slot
        self.squares[source] = piece
        self.squares[target] = captured
        if captured:
            captured_side = 1 if captured > 0 else 0
            captured_slot = self.undo_captured_slot[ply]
            swapped_square = self.undo_swapped_square[ply]
            self.piece_lists[captured_side].append(swapped_square)
            self.piece_lists[captured_side][captured_slot] = target
            self.piece_slots[target] = captured_slot
            if swapped_square != target:
                self.piece_slots[swapped_square] = len(self.piece_lists[captured_side]) - 1
            self.phase += PHASE_WEIGHTS[abs(captured)]
        else:
            self.piece_slots[target] = -1
        self.mg_score -= (
            MG_SCORES[piece + 7][target]
            - MG_SCORES[piece + 7][source]
            - MG_SCORES[captured + 7][target]
        )
        self.eg_score -= (
            EG_SCORES[piece + 7][target]
            - EG_SCORES[piece + 7][source]
            - EG_SCORES[captured + 7][target]
        )
        self.half_move_clock = self.undo_clock[ply]
        self.zobrist_key = self.undo_hash[ply]
        self.king_squares[True] = None if self.undo_red_king[ply] < 0 else self.undo_red_king[ply]
        self.king_squares[False] = None if self.undo_black_king[ply] < 0 else self.undo_black_king[ply]

    def evaluate(self):
        phase = max(0, min(16, self.phase))
        return (self.mg_score * phase + self.eg_score * (16 - phase)) // 16

    def is_in_check(self, is_red_turn):
        king = self.king_squares[is_red_turn]
        return king is None or self.is_square_attacked(king, not is_red_turn)

    def is_square_attacked(self, target, by_red):
        sign = 1 if by_red else -1
        for ray_index, ray in enumerate(RAYS[target]):
            blockers = 0
            for distance, source in enumerate(ray):
                piece = self.squares[source]
                if piece:
                    blockers += 1
                    if blockers == 1:
                        if piece == sign * Board.RED_CHARIOT:
                            return True
                        if piece == sign * Board.RED_KING and (
                            ray_index >= 2 or distance == 0
                        ):
                            return True
                    if blockers == 2:
                        if piece == sign * Board.RED_CANNON:
                            return True
                        break

        for source, leg in HORSE_ATTACKERS[target]:
            if (
                self.squares[source] == sign * Board.RED_HORSE
                and self.squares[leg] == Board.EMPTY
            ):
                return True

        for source in PAWN_ATTACKERS[by_red][target]:
            if self.squares[source] == sign * Board.RED_PAWN:
                return True
        return False
