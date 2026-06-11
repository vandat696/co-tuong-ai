import re

with open(r'c:\co-tuong-ai\backend\src\ai_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace piece saving to include old_clock
# Note: we need to be careful. The piece saving is always:
# piece = self.board.get_piece(from_row, from_col)
# captured_piece = self.board.get_piece(to_row, to_col)
# We can replace the captured_piece line with captured_piece + old_clock.

content = content.replace(
    "captured_piece = self.board.get_piece(to_row, to_col)",
    "captured_piece = self.board.get_piece(to_row, to_col)\n                old_clock = self.board.half_move_clock"
)

# Now replace the undo part
# self.board.set_piece(from_row, from_col, piece)
# self.board.set_piece(to_row, to_col, captured_piece)

content = content.replace(
    "self.board.set_piece(from_row, from_col, piece)\n                self.board.set_piece(to_row, to_col, captured_piece)",
    "self.board.undo_move(from_row, from_col, to_row, to_col, piece, captured_piece, old_clock)"
)

# Now I need to also implement stalemate, 3-fold repetition and draw rules in minimax.
# Let's write the whole modified ai_engine.py here? No, let's just do the undo refactor first.
# Wait, I also need to make sure I add `is_in_check` to MoveGenerator.

with open(r'c:\co-tuong-ai\backend\src\ai_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Refactored ai_engine.py undo moves")
