"""Move ordering heuristics for V3."""

from core.board import Board
from engines.v3.move import source_square, target_square

PIECE_VALUES = (0, 6000, 120, 120, 600, 270, 285, 30)


class MoveOrdering:
    def __init__(self, evaluator, max_ply):
        self.evaluator = evaluator
        self.max_ply = max_ply
        self.killers = [[None, None] for _ in range(max_ply)]
        self.history = [0] * (15 * 90)

    def clear(self):
        self.killers = [[None, None] for _ in range(self.max_ply)]
        self.history = [0] * (15 * 90)

    def ordered(
        self,
        position,
        moves,
        ply,
        preferred_move=None,
        checking_moves=None,
    ):
        return sorted(
            moves,
            key=lambda move: self.score(
                position,
                move,
                ply,
                preferred_move,
                checking_moves,
            ),
            reverse=True,
        )

    def score(
        self,
        position,
        move,
        ply,
        preferred_move=None,
        checking_moves=None,
    ):
        if move == preferred_move:
            return 1_000_000

        captured = position.squares[target_square(move)]
        if captured != Board.EMPTY:
            attacker = position.squares[source_square(move)]
            return (
                100_000
                + 10 * PIECE_VALUES[abs(captured)]
                - PIECE_VALUES[abs(attacker)]
            )

        if checking_moves is not None and move in checking_moves:
            return 95_000

        if ply < self.max_ply:
            if move == self.killers[ply][0]:
                return 90_000
            if move == self.killers[ply][1]:
                return 80_000

        piece = position.squares[source_square(move)]
        return self.history[(piece + 7) * 90 + target_square(move)]

    def record_quiet_cutoff(self, position, move, depth, ply):
        if ply < self.max_ply and move != self.killers[ply][0]:
            self.killers[ply][1] = self.killers[ply][0]
            self.killers[ply][0] = move

        piece = position.squares[source_square(move)]
        key = (piece + 7) * 90 + target_square(move)
        self.history[key] = min(75_000, self.history[key] + depth * depth)

    def is_killer(self, move, ply):
        return ply < self.max_ply and move in self.killers[ply]
