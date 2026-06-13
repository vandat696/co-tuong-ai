from core.board import Board
from engines.v3 import AIEngineV3
from engines.v3.engine import MATE_SCORE


def empty_board():
    board = Board()
    board.board = [[Board.EMPTY] * board.BOARD_COLS for _ in range(board.BOARD_ROWS)]
    board.half_move_clock = 0
    return board


def checkmated_black_board():
    board = empty_board()
    board.board[0][4] = Board.BLACK_KING
    board.board[1][3] = Board.RED_CHARIOT
    board.board[1][4] = Board.RED_CHARIOT
    board.board[1][5] = Board.RED_CHARIOT
    board.board[5][4] = Board.RED_PAWN
    board.board[9][4] = Board.RED_KING
    board.history = [board.get_state_hash()]
    return board


def test_depth_zero_recognizes_checkmate_before_evaluation():
    engine = AIEngineV3(checkmated_black_board(), max_depth=1, time_limit=10)
    engine.context.start()

    score = engine._negamax(0, -MATE_SCORE, MATE_SCORE, False, 1)

    assert score == -MATE_SCORE + 1


def test_quiescence_searches_non_capture_evasions_when_in_check():
    board = empty_board()
    board.board[0][4] = Board.BLACK_KING
    board.board[3][4] = Board.RED_CHARIOT
    board.board[5][4] = Board.RED_PAWN
    board.board[9][4] = Board.RED_KING
    board.history = [board.get_state_hash()]

    engine = AIEngineV3(board, max_depth=1, time_limit=10)
    engine.context.start()
    evasions = engine.context.legal_moves(False)

    assert evasions
    assert all(not engine.context.is_capture(move) for move in evasions)

    score = engine._quiescence(
        -MATE_SCORE,
        MATE_SCORE,
        False,
        1,
        evasions,
        True,
    )

    assert score > -MATE_SCORE + 1


def test_mate_score_prefers_faster_win():
    board = checkmated_black_board()
    engine = AIEngineV3(board, max_depth=1, time_limit=10)
    engine.context.start()

    mate_now = engine._negamax(0, -MATE_SCORE, MATE_SCORE, False, 1)
    mate_later = -MATE_SCORE + 5

    assert -mate_now > -mate_later


def test_engine_finds_mate_in_one_at_search_horizon():
    board = empty_board()
    board.board[0][4] = Board.BLACK_KING
    board.board[1][3] = Board.RED_CHARIOT
    board.board[1][4] = Board.BLACK_PAWN
    board.board[1][5] = Board.RED_CHARIOT
    board.board[2][4] = Board.RED_CHARIOT
    board.board[5][4] = Board.RED_PAWN
    board.board[9][4] = Board.RED_KING
    board.history = [board.get_state_hash()]

    engine = AIEngineV3(board, max_depth=1, time_limit=10)

    assert engine.get_best_move(True) == (2, 4, 1, 4)


def test_timeout_fallback_is_selected_by_evaluation_not_board_scan_order():
    engine = AIEngineV3(Board(), max_depth=5, time_limit=0)

    move = engine.get_best_move(True)

    assert move != (6, 0, 5, 0)
    assert move != (7, 1, 0, 1)
    assert engine.stats.used_fallback is True
    assert engine.stats.completed_depth == 0


def test_completed_iteration_reports_search_depth():
    engine = AIEngineV3(Board(), max_depth=1, time_limit=10)

    engine.get_best_move(True)

    assert engine.stats.used_fallback is False
    assert engine.stats.completed_depth == 1
