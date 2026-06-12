"""FastAPI server for the Xiangqi AI."""

import time
import json
import subprocess
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.ai_engine import AIEngine
from src.board import Board
from src.eval import Evaluator
from src.move_gen import MoveGenerator


AI_VERSIONS = {
    "python_current": {
        "id": "python_current",
        "order": 1,
        "name": "V1 - Minimax Alpha-Beta",
        "description": "Engine chính đang được phát triển trong dự án.",
        "engine": "Python",
        "runner": "python",
        "search": "Minimax, Alpha-Beta, đào sâu lặp, bảng chuyển vị, sắp xếp nước đi và tìm kiếm tĩnh.",
        "evaluation": "Tapered Evaluation theo khai/trung cuộc và tàn cuộc, kết hợp giá trị quân với bảng điểm vị trí.",
        "max_depth": 5,
        "time_limit": 0.5,
    },
    "wukong_reference": {
        "id": "wukong_reference",
        "order": 2,
        "name": "V2 - WukongJS Negamax",
        "description": "Engine WukongJS 1.0 dùng làm đối thủ tham chiếu cho AI Python.",
        "engine": "JavaScript / Node.js",
        "runner": "wukong",
        "search": "Negamax, Alpha-Beta, IDS, bảng chuyển vị, tìm kiếm tĩnh, Null Move, Futility, LMR và PVS.",
        "evaluation": "Giá trị quân cờ kết hợp bảng điểm vị trí (PST) lấy từ các tài liệu nghiên cứu cờ tướng.",
        "max_depth": 3,
        "time_limit": 0.0,
    },
}

WUKONG_BRIDGE = Path(__file__).parent / "references" / "wukong" / "bridge.js"


class GameStateRequest(BaseModel):
    board_state: List[List[int]]
    is_red_turn: bool
    half_move_clock: int = 0
    history: List[str] = Field(default_factory=list)


class MoveRequest(GameStateRequest):
    ai_version: str = "python_current"


class LegalMovesRequest(GameStateRequest):
    row: int
    col: int


class PlayerMoveRequest(GameStateRequest):
    from_row: int
    from_col: int
    to_row: int
    to_col: int


class GameStatus(BaseModel):
    checked_side: Optional[str] = None
    is_checkmate: bool = False
    winner: Optional[str] = None
    checked_king_pos: Optional[List[int]] = None


class StateResponse(BaseModel):
    half_move_clock: int
    history: List[str]
    status: GameStatus


class PlayerMoveResponse(StateResponse):
    from_row: int
    from_col: int
    to_row: int
    to_col: int


class LegalMovesResponse(BaseModel):
    moves: List[List[int]]
    status: GameStatus


class ValidateMoveResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None
    status: GameStatus


class MoveResponse(PlayerMoveResponse):
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
    return {"versions": versions, "default": "python_current"}


def build_board(request):
    board = Board()
    board.board = request.board_state
    board.half_move_clock = request.half_move_clock
    board.history = request.history or [board.get_state_hash()]
    return board


def allowed_moves_for_piece(board, row, col):
    return [
        (to_row, to_col)
        for to_row, to_col in MoveGenerator(board).generate_moves(row, col)
        if not board.would_repeat_threefold(row, col, to_row, to_col)
    ]


def has_allowed_move(board, is_red_turn):
    for row in range(board.BOARD_ROWS):
        for col in range(board.BOARD_COLS):
            piece = board.get_piece(row, col)
            if piece == Board.EMPTY or (piece > 0) != is_red_turn:
                continue
            if allowed_moves_for_piece(board, row, col):
                return True
    return False


def get_game_status(board, is_red_turn):
    side = "red" if is_red_turn else "black"
    opponent = "black" if is_red_turn else "red"
    move_gen = MoveGenerator(board)
    checked = move_gen.is_king_in_check(side)
    no_moves = not has_allowed_move(board, is_red_turn)
    return GameStatus(
        checked_side=side if checked else None,
        is_checkmate=no_moves,
        winner=opponent if no_moves else None,
        checked_king_pos=list(board.find_king(side)) if checked and board.find_king(side) else None,
    )


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


def first_allowed_move(board, is_red_turn):
    """Fallback for engines that do not understand the local repetition ban."""
    move_gen = MoveGenerator(board)
    for row in range(board.BOARD_ROWS):
        for col in range(board.BOARD_COLS):
            piece = board.get_piece(row, col)
            if piece == Board.EMPTY or (piece > 0) != is_red_turn:
                continue
            for to_row, to_col in move_gen.generate_moves(row, col):
                move = (row, col, to_row, to_col)
                if not board.would_repeat_threefold(*move):
                    return move
    return None


@app.post("/legal-moves", response_model=LegalMovesResponse)
def get_legal_moves(request: LegalMovesRequest):
    board = build_board(request)
    piece = board.get_piece(request.row, request.col)
    if piece == Board.EMPTY or (piece > 0) != request.is_red_turn:
        return LegalMovesResponse(
            moves=[],
            status=get_game_status(board, request.is_red_turn),
        )

    moves = allowed_moves_for_piece(board, request.row, request.col)
    return LegalMovesResponse(
        moves=[[row, col] for row, col in moves],
        status=get_game_status(board, request.is_red_turn),
    )


@app.post("/apply-move", response_model=PlayerMoveResponse)
def apply_player_move(request: PlayerMoveRequest):
    board = build_board(request)
    piece = board.get_piece(request.from_row, request.from_col)
    if piece == Board.EMPTY or (piece > 0) != request.is_red_turn:
        raise HTTPException(status_code=422, detail="Không đúng quân của bên đang đến lượt")

    allowed_moves = allowed_moves_for_piece(board, request.from_row, request.from_col)
    if (request.to_row, request.to_col) not in allowed_moves:
        raise HTTPException(status_code=422, detail="Nước đi không hợp lệ hoặc tạo lặp lần ba")

    board.move_piece(request.from_row, request.from_col, request.to_row, request.to_col)
    return PlayerMoveResponse(
        from_row=request.from_row,
        from_col=request.from_col,
        to_row=request.to_row,
        to_col=request.to_col,
        half_move_clock=board.half_move_clock,
        history=board.history,
        status=get_game_status(board, not request.is_red_turn),
    )


@app.post("/validate-move", response_model=ValidateMoveResponse)
def validate_player_move(request: PlayerMoveRequest):
    board = build_board(request)
    piece = board.get_piece(request.from_row, request.from_col)
    status = get_game_status(board, request.is_red_turn)
    if piece == Board.EMPTY or (piece > 0) != request.is_red_turn:
        return ValidateMoveResponse(
            valid=False,
            reason="Không đúng quân của bên đang đến lượt",
            status=status,
        )

    valid = (request.to_row, request.to_col) in allowed_moves_for_piece(
        board,
        request.from_row,
        request.from_col,
    )
    return ValidateMoveResponse(
        valid=valid,
        reason=None if valid else "Nước đi không hợp lệ hoặc tạo lặp lần ba",
        status=status,
    )


@app.post("/move", response_model=MoveResponse)
@app.post("/ai-move", response_model=MoveResponse)
def get_ai_move(request: MoveRequest):
    config = AI_VERSIONS.get(request.ai_version)
    if config is None:
        raise HTTPException(
            status_code=400,
            detail=f"Không tồn tại phiên bản AI: {request.ai_version}",
        )

    board = build_board(request)

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
    piece = board.get_piece(from_row, from_col)
    is_generated = (
        piece != Board.EMPTY
        and (piece > 0) == request.is_red_turn
        and (to_row, to_col) in move_gen.generate_moves(from_row, from_col)
    )
    if not is_generated or board.would_repeat_threefold(*best_move):
        if config["runner"] != "wukong":
            raise HTTPException(
                status_code=500,
                detail=f"AI trả về nước đi không hợp lệ hoặc tạo lặp lần ba: {best_move}",
            )

        best_move = first_allowed_move(board, request.is_red_turn)
        if best_move is None:
            raise HTTPException(status_code=422, detail="AI không còn nước đi không lặp hợp lệ")
        from_row, from_col, to_row, to_col = best_move

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
        status=get_game_status(board, not request.is_red_turn),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
