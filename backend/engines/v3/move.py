"""Compact integer move encoding used by the V3 search core."""

SQUARE_BITS = 7
SQUARE_MASK = (1 << SQUARE_BITS) - 1


def encode_move(source, target):
    return source | (target << SQUARE_BITS)


def source_square(move):
    return move & SQUARE_MASK


def target_square(move):
    return (move >> SQUARE_BITS) & SQUARE_MASK


def square(row, col):
    return row * 9 + col


def coordinates(index):
    return divmod(index, 9)


def move_from_coordinates(from_row, from_col, to_row, to_col):
    return encode_move(square(from_row, from_col), square(to_row, to_col))


def move_to_coordinates(move):
    return (*coordinates(source_square(move)), *coordinates(target_square(move)))
