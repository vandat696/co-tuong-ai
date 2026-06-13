"""Mobility and Xiangqi-specific piece activity features."""

from core.board import Board
from engines.v3.evaluation.types import TaperedScore


MOBILITY_WEIGHT = {
    Board.RED_HORSE: (2, 3),
    Board.RED_CANNON: (1, 1),
    Board.RED_CHARIOT: (1, 2),
}

HORSE_LEG_PENALTY = (7, 9)
ROOK_ENEMY_HALF_BONUS = (6, 4)
CANNON_TARGET_DIVISOR = 30
CANNON_KING_PRESSURE = (22, 14)


def evaluate_activity(board, move_gen, piece_values):
    mobility = TaperedScore()
    horse_activity = TaperedScore()
    rook_activity = TaperedScore()
    cannon_activity = TaperedScore()

    for row in range(board.BOARD_ROWS):
        for col in range(board.BOARD_COLS):
            piece = board.get_piece(row, col)
            piece_type = abs(piece)
            if piece == Board.EMPTY or piece_type not in MOBILITY_WEIGHT:
                continue

            sign = 1 if piece > 0 else -1
            pseudo_moves = move_gen._get_pseudo_moves(row, col, piece)
            mg_weight, eg_weight = MOBILITY_WEIGHT[piece_type]
            mobility.add(
                sign * len(pseudo_moves) * mg_weight,
                sign * len(pseudo_moves) * eg_weight,
            )

            if piece_type == Board.RED_HORSE:
                blocked_legs = _count_blocked_horse_legs(board, row, col)
                horse_activity.add(
                    -sign * blocked_legs * HORSE_LEG_PENALTY[0],
                    -sign * blocked_legs * HORSE_LEG_PENALTY[1],
                )
            elif piece_type == Board.RED_CHARIOT:
                if (piece > 0 and row <= 4) or (piece < 0 and row >= 5):
                    rook_activity.add(
                        sign * ROOK_ENEMY_HALF_BONUS[0],
                        sign * ROOK_ENEMY_HALF_BONUS[1],
                    )
            elif piece_type == Board.RED_CANNON:
                mg, eg = _cannon_pressure(board, row, col, piece, piece_values)
                cannon_activity.add(sign * mg, sign * eg)

    return {
        "mobility": mobility,
        "horse_activity": horse_activity,
        "rook_activity": rook_activity,
        "cannon_activity": cannon_activity,
    }


def _count_blocked_horse_legs(board, row, col):
    blocked = 0
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        leg_row, leg_col = row + dr, col + dc
        if (
            board._is_valid_pos(leg_row, leg_col)
            and board.get_piece(leg_row, leg_col) != Board.EMPTY
        ):
            blocked += 1
    return blocked


def _cannon_pressure(board, row, col, piece, piece_values):
    mg = 0
    eg = 0

    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        current_row, current_col = row + dr, col + dc
        found_screen = False

        while board._is_valid_pos(current_row, current_col):
            target = board.get_piece(current_row, current_col)
            if target == Board.EMPTY:
                current_row += dr
                current_col += dc
                continue

            if not found_screen:
                found_screen = True
                current_row += dr
                current_col += dc
                continue

            if target * piece < 0:
                if abs(target) == Board.RED_KING:
                    mg += CANNON_KING_PRESSURE[0]
                    eg += CANNON_KING_PRESSURE[1]
                else:
                    pressure = piece_values.get(abs(target), 0) // CANNON_TARGET_DIVISOR
                    mg += pressure
                    eg += pressure
            break

    return mg, eg
