from src.board import Board
from src.engine_v3 import AIEngineV3
from src.engine_v3.engine import MATE_SCORE, MATE_THRESHOLD
from src.engine_v3.transposition import EXACT, TranspositionTable


def test_zobrist_hash_updates_and_restores_with_move():
    board = Board()
    engine = AIEngineV3(board, time_limit=10)
    engine.context.start()
    original_key = engine.context.zobrist_key
    move = engine.context.legal_moves(True)[0]

    undo = engine.context.push(move)

    assert engine.context.zobrist_key == engine.context.zobrist.hash_board(board)

    engine.context.pop(undo)

    assert engine.context.zobrist_key == original_key
    assert engine.context.zobrist_key == engine.context.zobrist.hash_board(board)


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

    engine.ordering.record_quiet_cutoff(board, cutoff_move, depth=4, ply=2)
    ordered = engine.ordering.ordered(board, quiet_moves, ply=2)

    assert engine.ordering.is_killer(cutoff_move, 2)
    assert ordered[0] == cutoff_move
