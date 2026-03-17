"""
api.py - FastAPI server cho cờ tướng AI
"""


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from src.board import Board
from src.move_gen import MoveGenerator
from src.ai_engine import AIEngine
from src.eval import Evaluator


# ===== Pydantic Models =====

class MoveRequest(BaseModel):
    """Request body cho /move endpoint"""
    board_state: List[List[int]]  # Mảng 10x9
    is_red_turn: bool  # True = lượt Đỏ


class MoveResponse(BaseModel):
    """Response từ /move endpoint"""
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    score: int


# ===== FastAPI App =====

app = FastAPI(title="Xiangqi AI", version="1.0.0")

# TODO: Thêm CORS middleware để frontend có thể gọi API
# Giải thích: CORS (Cross-Origin Resource Sharing) cho phép frontend (khác origin) gọi backend
# Cấu trúc:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cho phép tất cả origin (dev), trong prod nên cụ thể
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Endpoints =====

@app.get("/")
def health_check():
    """
    Endpoint kiểm tra API có hoạt động không
    
    Return:
        dict: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/move", response_model=MoveResponse)
def get_ai_move(request: MoveRequest):
    """
    Endpoint chính: AI tính nước đi tốt nhất
    
    Args:
        request (MoveRequest): 
            - board_state: Mảng 10x9 của bàn cờ
            - is_red_turn: True = lượt Đỏ
    
    Return:
        MoveResponse: 
            - from_row, from_col: Vị trí quân cần di chuyển
            - to_row, to_col: Vị trí đích
            - score: Điểm số đánh giá
    """
    # Tạo Board từ board_state
    board = Board()
    board.board = request.board_state

    # Tạo AIEngine và tìm nước đi tốt nhất
    engine = AIEngine(board, max_depth=2)
    best_move = engine.get_best_move(request.is_red_turn)
    
    if best_move is None:
        raise Exception("Không có nước đi hợp lệ")
    
    from_row, from_col, to_row, to_col = best_move
    
    # Tính điểm số hiện tại
    evaluator = Evaluator(board)
    score = evaluator.evaluate()
    
    return MoveResponse(
        from_row=from_row,
        from_col=from_col,
        to_row=to_row,
        to_col=to_col,
        score=score
    )


# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)