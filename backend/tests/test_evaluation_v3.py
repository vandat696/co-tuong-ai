from core.board import Board
from engines.v3.evaluation import EvaluatorV3


def board_with_kings():
    board = Board()
    board.board = [[Board.EMPTY] * board.BOARD_COLS for _ in range(board.BOARD_ROWS)]
    board.board[9][4] = Board.RED_KING
    board.board[0][3] = Board.BLACK_KING
    board.history = [board.get_state_hash()]
    return board


def evaluate(board):
    return EvaluatorV3(board).evaluate_breakdown()


def test_blocked_horse_scores_lower_than_free_horse():
    free = board_with_kings()
    free.board[5][4] = Board.RED_HORSE

    blocked = board_with_kings()
    blocked.board[5][4] = Board.RED_HORSE
    blocked.board[4][4] = Board.RED_PAWN
    blocked.board[6][4] = Board.RED_PAWN
    blocked.board[5][3] = Board.RED_PAWN
    blocked.board[5][5] = Board.RED_PAWN

    free_score = evaluate(free)
    blocked_score = evaluate(blocked)

    assert blocked_score["horse_activity"] < free_score["horse_activity"]
    assert blocked_score["mobility"] < free_score["mobility"]


def test_advanced_rook_gets_activity_bonus():
    home = board_with_kings()
    home.board[8][0] = Board.RED_CHARIOT

    advanced = board_with_kings()
    advanced.board[4][0] = Board.RED_CHARIOT

    assert evaluate(advanced)["rook_activity"] > evaluate(home)["rook_activity"]


def test_cannon_screen_toward_enemy_king_gets_pressure_bonus():
    inactive = board_with_kings()
    inactive.board[5][3] = Board.RED_CANNON

    pressured = board_with_kings()
    pressured.board[5][3] = Board.RED_CANNON
    pressured.board[2][3] = Board.RED_PAWN

    assert evaluate(pressured)["cannon_activity"] > evaluate(inactive)["cannon_activity"]


def test_advisors_and_elephants_improve_king_safety():
    exposed = board_with_kings()

    defended = board_with_kings()
    defended.board[9][3] = Board.RED_ADVISOR
    defended.board[9][5] = Board.RED_ADVISOR
    defended.board[7][2] = Board.RED_ELEPHANT
    defended.board[7][6] = Board.RED_ELEPHANT

    assert evaluate(defended)["king_safety"] > evaluate(exposed)["king_safety"]


def test_breakdown_total_matches_feature_sum():
    board = Board()
    breakdown = evaluate(board)

    assert breakdown["total"] == sum(
        value for name, value in breakdown.items() if name != "total"
    )
