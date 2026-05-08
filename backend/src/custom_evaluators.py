from src.eval import Evaluator
import numpy as np
import torch

class HeuristicEvaluatorWrapper:
    def __init__(self, board):
        self.board = board
        self.base_evaluator = Evaluator(board)

    def evaluate(self, side_to_move=None):
        return self.base_evaluator.evaluate()

    def get_piece_value(self, piece):
        return self.base_evaluator.get_piece_value(piece)

class MLEvaluatorWrapper:
    def __init__(self, board, model, model_type="mlp", device="cpu", scale=1000.0):
        self.board = board
        self.model = model
        self.model_type = model_type
        self.device = device
        self.scale = scale
        self.base_evaluator = Evaluator(board)  # dùng cho get_piece_value

    def encode_board(self, board_np, side_to_move):
        PIECE_TO_PLANE = {
            -7: 0, -6: 1, -5: 2, -4: 3, -3: 4, -2: 5, -1: 6,
             1: 7,  2: 8,  3: 9,  4: 10, 5: 11, 6: 12, 7: 13,
        }
        x = np.zeros((15, 10, 9), dtype=np.float32)

        for r in range(10):
            for c in range(9):
                piece = int(board_np[r][c])
                if piece != 0:
                    x[PIECE_TO_PLANE[piece], r, c] = 1.0

        x[14, :, :] = 1.0 if side_to_move == "red" else 0.0
        return x

    def evaluate(self, side_to_move=None):
        if side_to_move is None:
            side_to_move = "red"

        board_np = np.array(self.board.board, dtype=np.int8)
        x = self.encode_board(board_np, side_to_move)

        xt = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(self.device)

        if self.model_type == "mlp":
            xt = xt.view(xt.shape[0], -1)

        self.model.eval()
        with torch.no_grad():
            pred = self.model(xt).item()

        return float(pred * self.scale)

    def get_piece_value(self, piece):
        return self.base_evaluator.get_piece_value(piece)

class HybridEvaluatorWrapper:
    def __init__(self, board, model, model_type="mlp", device="cpu", alpha=0.5, scale=1000.0):
        self.board = board
        self.alpha = alpha
        self.heuristic = Evaluator(board)
        self.ml_eval = MLEvaluatorWrapper(
            board=board,
            model=model,
            model_type=model_type,
            device=device,
            scale=scale,
        )

    def evaluate(self, side_to_move=None):
        heur_score = self.heuristic.evaluate()
        ml_score = self.ml_eval.evaluate(side_to_move=side_to_move)
        return self.alpha * ml_score + (1 - self.alpha) * heur_score

    def get_piece_value(self, piece):
        return self.heuristic.get_piece_value(piece)