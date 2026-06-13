"""Composite V3 evaluator with explainable feature breakdown."""

from src.eval import Evaluator
from src.engine_v3.evaluation.activity import evaluate_activity
from src.engine_v3.evaluation.king_safety import evaluate_king_safety
from src.move_gen import MoveGenerator


class EvaluatorV3(Evaluator):
    """V1 tapered material/PST plus dynamic Xiangqi positional features."""

    def __init__(self, board):
        super().__init__(board)
        self.move_gen = MoveGenerator(board)

    def evaluate(self):
        return self.evaluate_breakdown()["total"]

    def evaluate_fast(self):
        """Cheap tapered material/PST score for deep search nodes."""
        return super().evaluate()

    def evaluate_breakdown(self):
        phase = max(0, min(16, self.phase))
        base = super().evaluate()
        features = evaluate_activity(
            self.board,
            self.move_gen,
            self.MG_PIECE_VALUES,
        )
        features["king_safety"] = evaluate_king_safety(self.board, self.move_gen)

        breakdown = {"base": base}
        for name, score in features.items():
            breakdown[name] = score.tapered(phase)
        breakdown["total"] = sum(breakdown.values())
        return breakdown
