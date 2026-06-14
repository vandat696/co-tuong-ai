from core.board import Board
from engines.v3 import AIEngineV3
from engines.v3.engine import MATE_SCORE, MATE_THRESHOLD
from engines.v3.move import move_from_coordinates, move_to_coordinates, target_square
from engines.v3.opening import opening_moves
from engines.v3.transposition import EXACT, TranspositionTable
from core.move_gen import MoveGenerator


def test_zobrist_hash_updates_and_restores_with_move():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    original_key = engine.context.zobrist_key
    move = engine.context.legal_moves(True)[0]

    undo = engine.context.push(move)

    assert engine.context.zobrist_key == engine.context.zobrist.hash_squares(
        engine.context.position.squares
    )

    engine.context.pop(undo)

    assert engine.context.zobrist_key == original_key
    assert engine.context.zobrist_key == engine.context.zobrist.hash_squares(
        engine.context.position.squares
    )


def test_transposition_table_normalizes_mate_distance():
    table = TranspositionTable(capacity=8, mate_threshold=MATE_THRESHOLD)
    score = MATE_SCORE - 3

    table.store(5, depth=4, score=score, flag=EXACT, best_move=None, ply=3)
    entry = table.probe(5)

    assert table.read_score(entry, ply=3) == score
    assert table.read_score(entry, ply=5) == MATE_SCORE - 5


def test_killer_and_history_prioritize_quiet_cutoff():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    quiet_moves = [
        move for move in engine.context.legal_moves(True)
        if not engine.context.is_capture(move)
    ]
    cutoff_move = quiet_moves[-1]

    engine.ordering.record_quiet_cutoff(
        engine.context.position, cutoff_move, depth=4, ply=2
    )
    ordered = engine.ordering.ordered(engine.context.position, quiet_moves, ply=2)

    assert engine.ordering.is_killer(cutoff_move, 2)
    assert ordered[0] == cutoff_move


def test_evaluation_cache_reuses_same_zobrist_position():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()

    first = engine.context.evaluate_for_side(True, dynamic=True)
    engine.context.evaluator.evaluate = lambda: (_ for _ in ()).throw(
        AssertionError("dynamic evaluation should have been cached")
    )

    assert engine.context.evaluate_for_side(True, dynamic=True) == first
    assert engine.context.evaluate_for_side(False, dynamic=True) == -first


def test_fast_evaluation_cache_reuses_same_zobrist_position():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()

    first = engine.context.evaluate_for_side(True)
    engine.context.evaluator.evaluate_fast = lambda: (_ for _ in ()).throw(
        AssertionError("fast evaluation should have been cached")
    )

    assert engine.context.evaluate_for_side(True) == first
    assert engine.context.evaluate_for_side(False) == -first


def test_capture_only_move_generation_is_subset_of_legal_moves():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()

    all_moves = set(engine.context.legal_moves(True))
    captures = set(engine.context.legal_moves(True, captures_only=True))

    assert captures <= all_moves
    assert all(
        engine.context.position.squares[target_square(move)] != Board.EMPTY
        for move in captures
    )


def test_fast_move_generation_matches_authoritative_generator():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    authoritative = MoveGenerator(board)
    expected = set()

    for row in range(board.BOARD_ROWS):
        for col in range(board.BOARD_COLS):
            piece = board.get_piece(row, col)
            if piece > 0:
                expected.update(
                    move_from_coordinates(row, col, to_row, to_col)
                    for to_row, to_col in authoritative.generate_moves(row, col)
                )

    assert set(engine.context.legal_moves(True)) == expected


def test_search_push_pop_does_not_serialize_board_history():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    original_history = list(board.history)
    original_counts = engine.context.repetition_counts.copy()

    undo = engine.context.push(engine.context.legal_moves(True)[0])
    engine.context.pop(undo)

    assert board.history == original_history
    assert engine.context.repetition_counts == original_counts


def test_v3_search_core_uses_flat_board_and_integer_moves():
    engine = AIEngineV3(Board(), time_limit=10)
    engine.context.start()
    moves = engine.context.legal_moves(True)

    assert len(engine.context.position.squares) == 90
    assert all(isinstance(move, int) for move in moves)
    assert all(len(move_to_coordinates(move)) == 4 for move in moves)


def test_opening_book_prioritizes_conventional_starting_moves():
    engine = AIEngineV3(Board(), time_limit=10)
    engine.context.start()

    book = opening_moves(engine.context.position, True)
    ordered = engine.ordering.ordered(
        engine.context.position,
        engine.context.pseudo_moves(True),
        ply=0,
        opening_moves=book,
    )

    assert move_to_coordinates(book[0]) == (7, 7, 7, 4)
    assert ordered[0] == book[0]


def test_opening_book_has_screen_horse_reply_to_central_cannon():
    board = Board()
    board.move_piece(7, 7, 7, 4)
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()

    replies = {
        move_to_coordinates(move)
        for move in opening_moves(engine.context.position, False)
    }

    assert (0, 1, 2, 2) in replies
    assert (0, 7, 2, 6) in replies


def test_opening_book_keeps_root_choice_inside_book():
    engine = AIEngineV3(Board(), max_depth=4, time_limit=10)

    move = move_from_coordinates(*engine.get_best_move(True))

    assert move in engine.root_opening_moves


def test_position_piece_lists_and_incremental_evaluation_restore_after_move():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    position = engine.context.position
    original_lists = [pieces[:] for pieces in position.piece_lists]
    original_score = position.evaluate()
    move = engine.context.legal_moves(True)[0]

    assert position.make_move(move, True)
    position.unmake_move()

    assert position.piece_lists == original_lists
    assert position.evaluate() == original_score
    assert position.undo_ply == 0


def test_search_evaluation_rewards_free_horse_over_blocked_horse():
    free = Board()
    free.board = [[Board.EMPTY] * free.BOARD_COLS for _ in range(free.BOARD_ROWS)]
    free.board[0][3] = Board.BLACK_KING
    free.board[9][4] = Board.RED_KING
    free.board[5][4] = Board.RED_HORSE
    free.history = [free.get_state_hash()]

    blocked = Board()
    blocked.board = [row[:] for row in free.board]
    blocked.board[4][4] = Board.RED_PAWN
    blocked.board[6][4] = Board.RED_PAWN
    blocked.history = [blocked.get_state_hash()]

    free_engine = AIEngineV3(free, time_limit=10)
    blocked_engine = AIEngineV3(blocked, time_limit=10)
    free_engine.context.start()
    blocked_engine.context.start()

    free_activity = (
        free_engine.context.position.evaluate_search()
        - free_engine.context.position.evaluate()
    )
    blocked_activity = (
        blocked_engine.context.position.evaluate_search()
        - blocked_engine.context.position.evaluate()
    )

    assert free_activity > blocked_activity


def test_v2_inspired_pawn_pst_rewards_deep_advanced_pawn():
    home = Board()

    advanced = Board()
    advanced.board = [row[:] for row in home.board]
    advanced.board[6][4] = Board.EMPTY
    advanced.board[1][4] = Board.RED_PAWN
    advanced.history = [advanced.get_state_hash()]

    home_engine = AIEngineV3(home, time_limit=10)
    advanced_engine = AIEngineV3(advanced, time_limit=10)
    home_engine.context.start()
    advanced_engine.context.start()

    assert (
        advanced_engine.context.position.evaluate()
        - home_engine.context.position.evaluate()
        >= 100
    )


def test_checking_quiet_move_is_ordered_before_other_quiet_moves():
    board = Board()
    board.board = [[Board.EMPTY] * board.BOARD_COLS for _ in range(board.BOARD_ROWS)]
    board.board[0][4] = Board.BLACK_KING
    board.board[5][3] = Board.RED_CHARIOT
    board.board[9][4] = Board.RED_KING
    board.history = [board.get_state_hash()]
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    moves = engine.context.pseudo_moves(True)
    checks = engine._checking_moves(moves, True)
    ordered = engine.ordering.ordered(
        engine.context.position,
        moves,
        ply=0,
        checking_moves=checks,
    )

    assert checks
    assert ordered[0] in checks
