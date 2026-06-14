"""Engine V4 - NNUE Evaluation Engine."""

from engines.v3.engine import AIEngineV3
from engines.v3.context import SearchContext

class AIEngineV4(AIEngineV3):
    """
    V4 Search Engine.
    Extends V3 but injects NNUE evaluation into the search context.
    """
    NNUE_MODEL_PATH = "ml/models/xiangqi.nnue"
    
    def __init__(self, board, max_depth=5, time_limit=1.0, tt_capacity=65_536):
        # Initialize V3 base (this sets up self.context as a V3 context)
        super().__init__(board, max_depth, time_limit, tt_capacity)
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) # project root
        model_path = os.path.join(base_dir, "ml", "models", "xiangqi.nnue")
        self.context = SearchContext(board, time_limit, nnue_path=model_path)
