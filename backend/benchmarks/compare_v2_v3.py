"""Repeatable same-time benchmark for Wukong V2 and Python V3."""

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path


BACKEND = Path(__file__).resolve().parents[1]
ROOT = BACKEND.parent
sys.path.insert(0, str(BACKEND))

from api import WUKONG_BRIDGE, board_to_fen  # noqa: E402
from core.board import Board  # noqa: E402
from engines.v3 import AIEngineV3  # noqa: E402


def benchmark_v2(runs, time_limit):
    fen = board_to_fen(Board().board, True, 0)
    results = []
    for _ in range(runs):
        completed = subprocess.run(
            [
                "node",
                str(WUKONG_BRIDGE),
                fen,
                "64",
                str(round(time_limit * 1000)),
            ],
            cwd=ROOT,
            capture_output=True,
            check=True,
            text=True,
        )
        data = json.loads(completed.stdout)
        results.append(
            {
                "elapsed_ms": data["search_elapsed_ms"],
                "depth": data["completed_depth"],
                "nodes": data["nodes"],
                "move": [
                    data["from_row"],
                    data["from_col"],
                    data["to_row"],
                    data["to_col"],
                ],
            }
        )
    return results


def benchmark_v3(runs, time_limit):
    results = []
    for _ in range(runs):
        engine = AIEngineV3(Board(), max_depth=64, time_limit=time_limit)
        started = time.perf_counter()
        move = engine.get_best_move(True)
        results.append(
            {
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
                "depth": engine.stats.completed_depth,
                "nodes": engine.stats.nodes + engine.stats.qnodes,
                "move": list(move),
            }
        )
    return results


def summarize(results):
    return {
        "runs": len(results),
        "average_ms": round(statistics.mean(item["elapsed_ms"] for item in results), 2),
        "average_depth": round(statistics.mean(item["depth"] for item in results), 2),
        "average_nodes": round(statistics.mean(item["nodes"] for item in results)),
        "depths": [item["depth"] for item in results],
        "moves": [item["move"] for item in results],
    }


if __name__ == "__main__":
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    time_limit = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5
    print(
        json.dumps(
            {
                "time_limit_seconds": time_limit,
                "v2": summarize(benchmark_v2(runs, time_limit)),
                "v3": summarize(benchmark_v3(runs, time_limit)),
            },
            indent=2,
        )
    )
