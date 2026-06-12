"""FastAPI server for the Xiangqi AI."""

import time
import json
import subprocess
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.ai_engine import AIEngine
from src.board import Board
from src.eval import Evaluator
from src.move_gen import MoveGenerator


AI_VERSIONS = {
    "v1_initial": {
        "id": "v1_initial",
        "order": 1,
        "name": "V1 - AI ban đầu",
        "description": "Mô phỏng cột mốc đầu tiên của dự án bằng engine Python với độ sâu nhỏ.",
        "engine": "Python",
        "runner": "python",
        "search": "Minimax, cắt tỉa Alpha-Beta và sắp xếp nước đi.",
        "evaluation": "Giá trị quân cờ và bảng điểm vị trí; dùng cùng bộ đánh giá hiện tại để mô phỏng.",
        "max_depth": 2,
        "time_limit": 0.15,
    },
    "v2_current": {
        "id": "v2_current",
        "order": 2,
        "name": "V2 - AI Python hiện tại",
        "description": "Phiên bản chính đang được phát triển trong dự án.",
        "engine": "Python",
        "runner": "python",
        "search": "Minimax, Alpha-Beta, đào sâu lặp, bảng chuyển vị, sắp xếp nước đi và tìm kiếm tĩnh.",
        "evaluation": "Tapered Evaluation theo khai/trung cuộc và tàn cuộc, kết hợp giá trị quân với bảng điểm vị trí.",
        "max_depth": 5,
        "time_limit": 0.5,
    },
    "v3_wukong": {
        "id": "v3_wukong",
        "order": 3,
        "name": "V3 - WukongJS tham khảo",
        "description": "Engine WukongJS 1.0 dùng làm đối thủ tham chiếu cho AI Python.",
        "engine": "JavaScript / Node.js",
        "runner": "wukong",
        "search": "Negamax, Alpha-Beta, đào sâu lặp, bảng chuyển vị, tìm kiếm tĩnh, Null Move, Futility, LMR và PVS.",
        "evaluation": "Giá trị quân cờ kết hợp bảng điểm vị trí (PST) lấy từ các tài liệu nghiên cứu cờ tướng.",
        "max_depth": 3,
        "time_limit": 0.0,
    },
}

WUKONG_BRIDGE = Path(__file__).parent / "references" / "wukong" / "bridge.js"


class MoveRequest(BaseModel):
    board_state: List[List[int]]
    is_red_turn: bool
    ai_version: str = "v2_current"
    half_move_clock: int = 0
    history: List[str] = Field(default_factory=list)


class MoveResponse(BaseModel):
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    score: int
    half_move_clock: int
    history: List[str]
    ai_version: str
    ai_name: str
    max_depth: int
    time_limit: float
    elapsed_ms: float


app = FastAPI(title="Xiangqi AI", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.get("/ai-versions")
def get_ai_versions():
    """Return AI configurations that can be selected by the frontend."""
    versions = sorted(AI_VERSIONS.values(), key=lambda item: item["order"])
    return {"versions": versions, "default": "v2_current"}


def board_to_fen(board_state, is_red_turn, half_move_clock):
    piece_chars = {
        1: "K", 2: "A", 3: "B", 4: "R", 5: "N", 6: "C", 7: "P",
        -1: "k", -2: "a", -3: "b", -4: "r", -5: "n", -6: "c", -7: "p",
    }
    ranks = []
    for row in board_state:
        rank = ""
        empty_count = 0
        for piece in row:
            if piece == 0:
                empty_count += 1
                continue
            if empty_count:
                rank += str(empty_count)
                empty_count = 0
            rank += piece_chars[piece]
        if empty_count:
            rank += str(empty_count)
        ranks.append(rank)

    side = "w" if is_red_turn else "b"
    return f"{'/'.join(ranks)} {side} - - {half_move_clock} 1"


def get_wukong_move(request, config):
    fen = board_to_fen(
        request.board_state,
        request.is_red_turn,
        request.half_move_clock,
    )
    try:
        result = subprocess.run(
            ["node", str(WUKONG_BRIDGE), fen, str(config["max_depth"])],
            capture_output=True,
            check=True,
            text=True,
            timeout=15,
        )
        move = json.loads(result.stdout)
    except (FileNotFoundError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        raise HTTPException(
            status_code=503,
            detail=f"Không thể chạy WukongJS: {error}",
        ) from error

    return (
        move["from_row"],
        move["from_col"],
        move["to_row"],
        move["to_col"],
    )


@app.post("/move", response_model=MoveResponse)
def get_ai_move(request: MoveRequest):
    config = AI_VERSIONS.get(request.ai_version)
    if config is None:
        raise HTTPException(
            status_code=400,
            detail=f"Không tồn tại phiên bản AI: {request.ai_version}",
        )

    board = Board()
    board.board = request.board_state
    board.half_move_clock = request.half_move_clock
    board.history = request.history or [board.get_state_hash()]

    started_at = time.perf_counter()
    if config["runner"] == "wukong":
        best_move = get_wukong_move(request, config)
    else:
        engine = AIEngine(
            board,
            max_depth=config["max_depth"],
            time_limit=config["time_limit"],
        )
        best_move = engine.get_best_move(request.is_red_turn)
    elapsed_ms = (time.perf_counter() - started_at) * 1000

    if best_move is None:
        raise HTTPException(status_code=422, detail="AI không tìm được nước đi hợp lệ")

    from_row, from_col, to_row, to_col = best_move
    move_gen = MoveGenerator(board)
    if (to_row, to_col) not in move_gen.generate_moves(from_row, from_col):
        raise HTTPException(
            status_code=500,
            detail=f"AI trả về nước đi không hợp lệ: {best_move}",
        )

    board.move_piece(from_row, from_col, to_row, to_col)
    score = Evaluator(board).evaluate()

    return MoveResponse(
        from_row=from_row,
        from_col=from_col,
        to_row=to_row,
        to_col=to_col,
        score=score,
        half_move_clock=board.half_move_clock,
        history=board.history,
        ai_version=config["id"],
        ai_name=config["name"],
        max_depth=config["max_depth"],
        time_limit=config["time_limit"],
        elapsed_ms=round(elapsed_ms, 2),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
