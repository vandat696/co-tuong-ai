import time
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.board import Board
from engines.v4.engine_v4 import AIEngineV4
from engines.v3.engine import AIEngineV3

def run_benchmark():
    print("=== Xiangqi AI Benchmark ===")
    
    board = Board()
    
    # 1. Benchmark V3 (Heuristic)
    print("\n[V3 Engine - Heuristic Evaluation]")
    v3_engine = AIEngineV3(board, max_depth=5, time_limit=5.0)
    
    start_v3 = time.perf_counter()
    best_move_v3 = v3_engine.get_best_move(True)
    end_v3 = time.perf_counter()
    
    time_v3 = end_v3 - start_v3
    nodes_v3 = v3_engine.stats.nodes
    nps_v3 = nodes_v3 / time_v3 if time_v3 > 0 else 0
    
    print(f"Move: {best_move_v3}")
    print(f"Depth reached: {v3_engine.stats.completed_depth}")
    print(f"Nodes searched: {nodes_v3:,}")
    print(f"Time taken: {time_v3:.3f}s")
    print(f"NPS: {nps_v3:,.0f} nodes/sec")
    
    # 2. Benchmark V4 (NNUE)
    print("\n[V4 Engine - NNUE Evaluation]")
    
    # Point to the trained model
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    model_path = os.path.join(base_dir, "ml", "models", "xiangqi.nnue")
    AIEngineV4.NNUE_MODEL_PATH = "ml/models/xiangqi.nnue"
    
    v4_engine = AIEngineV4(board, max_depth=5, time_limit=5.0)
    
    start_v4 = time.perf_counter()
    best_move_v4 = v4_engine.get_best_move(True)
    end_v4 = time.perf_counter()
    
    time_v4 = end_v4 - start_v4
    nodes_v4 = v4_engine.stats.nodes
    nps_v4 = nodes_v4 / time_v4 if time_v4 > 0 else 0
    
    print(f"Move: {best_move_v4}")
    print(f"Depth reached: {v4_engine.stats.completed_depth}")
    print(f"Nodes searched: {nodes_v4:,}")
    print(f"Time taken: {time_v4:.3f}s")
    print(f"NPS: {nps_v4:,.0f} nodes/sec")
    
    print("\n=== Summary ===")
    print(f"V3 NPS: {nps_v3:,.0f}")
    print(f"V4 NPS: {nps_v4:,.0f}")
    
    if nps_v3 > 0 and nps_v4 > 0:
        ratio = nps_v4 / nps_v3
        print(f"NNUE speed is {ratio:.2f}x of Heuristic speed.")

if __name__ == "__main__":
    run_benchmark()
