"""Small, conservative Xiangqi opening book for root move ordering."""

from core.board import Board
from engines.v3.move import move_from_coordinates


def _position_key(board):
    return tuple(piece for row in board.board for piece in row)


def _after(*moves):
    board = Board()
    for move in moves:
        board.move_piece(*move)
    return _position_key(board)


START = _position_key(Board())

# Ordered by conventional opening value. Search may still reject these moves.
OPENING_BOOK = {
    (START, True): (
        (7, 7, 7, 4),  # Central cannon
        (7, 1, 7, 4),
        (9, 7, 7, 6),  # Develop horse
        (9, 1, 7, 2),
        (6, 6, 5, 6),  # Pawn opening
        (6, 2, 5, 2),
    ),
    (_after((7, 7, 7, 4)), False): (
        (0, 1, 2, 2),  # Screen horse against central cannon
        (0, 7, 2, 6),
        (3, 6, 4, 6),
        (3, 2, 4, 2),
    ),
    (_after((7, 1, 7, 4)), False): (
        (0, 7, 2, 6),
        (0, 1, 2, 2),
        (3, 2, 4, 2),
        (3, 6, 4, 6),
    ),
    (_after((9, 7, 7, 6)), False): (
        (0, 1, 2, 2),
        (0, 7, 2, 6),
        (2, 7, 2, 4),
    ),
    (_after((9, 1, 7, 2)), False): (
        (0, 7, 2, 6),
        (0, 1, 2, 2),
        (2, 1, 2, 4),
    ),
    (_after((6, 6, 5, 6)), False): (
        (3, 6, 4, 6),
        (0, 1, 2, 2),
        (2, 7, 2, 4),
    ),
    (_after((6, 2, 5, 2)), False): (
        (3, 2, 4, 2),
        (0, 7, 2, 6),
        (2, 1, 2, 4),
    ),
}


def opening_moves(position, is_red_turn):
    """Return legal book moves in preference order for the current position."""
    coordinates = OPENING_BOOK.get((tuple(position.squares), is_red_turn), ())
    pseudo_moves = set(position.generate_moves(is_red_turn))
    return tuple(
        move
        for move in (move_from_coordinates(*coords) for coords in coordinates)
        if move in pseudo_moves
    )
