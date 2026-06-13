"""King safety and palace-defense features."""

from core.board import Board
from engines.v3.evaluation.types import TaperedScore


DEFENDER_NEAR_KING_BONUS = (7, 3)
MISSING_DEFENDER_PENALTY = (8, 2)
CHECK_PENALTY = (35, 20)
PALACE_ATTACKER_PENALTY = (8, 5)


def evaluate_king_safety(board, move_gen):
    score = TaperedScore()
    for is_red in (True, False):
        sign = 1 if is_red else -1
        color = "red" if is_red else "black"
        king = board.find_king(color)
        if king is None:
            continue

        defenders = _defenders(board, is_red)
        near_king = sum(
            1
            for row, col, _ in defenders
            if abs(row - king[0]) <= 2 and abs(col - king[1]) <= 2
        )
        missing = 4 - len(defenders)
        attackers = _attackers_near_palace(board, is_red)

        mg = (
            near_king * DEFENDER_NEAR_KING_BONUS[0]
            - missing * MISSING_DEFENDER_PENALTY[0]
            - attackers * PALACE_ATTACKER_PENALTY[0]
        )
        eg = (
            near_king * DEFENDER_NEAR_KING_BONUS[1]
            - missing * MISSING_DEFENDER_PENALTY[1]
            - attackers * PALACE_ATTACKER_PENALTY[1]
        )
        if move_gen.is_king_in_check(color):
            mg -= CHECK_PENALTY[0]
            eg -= CHECK_PENALTY[1]

        score.add(sign * mg, sign * eg)
    return score


def _defenders(board, is_red):
    defenders = []
    for row in range(board.BOARD_ROWS):
        for col in range(board.BOARD_COLS):
            piece = board.get_piece(row, col)
            if (piece > 0) != is_red:
                continue
            if abs(piece) in (Board.RED_ADVISOR, Board.RED_ELEPHANT):
                defenders.append((row, col, piece))
    return defenders


def _attackers_near_palace(board, target_is_red):
    palace_rows = range(7, 10) if target_is_red else range(0, 3)
    extended_rows = range(5, 10) if target_is_red else range(0, 5)
    count = 0

    for row in extended_rows:
        for col in range(1, 8):
            piece = board.get_piece(row, col)
            if piece == Board.EMPTY or (piece > 0) == target_is_red:
                continue
            piece_type = abs(piece)
            if piece_type in (Board.RED_CHARIOT, Board.RED_CANNON, Board.RED_HORSE):
                distance_to_palace = min(abs(row - palace_row) for palace_row in palace_rows)
                if distance_to_palace <= 2:
                    count += 1
    return count
