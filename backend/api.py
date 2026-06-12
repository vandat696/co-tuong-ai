"""FastAPI server cho cờ tướng AI.

Module này cung cấp các REST API endpoint để tương tác với AI Engine cờ tướng,
nhận trạng thái bàn cờ từ client và trả về nước đi tính toán được.
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
    """Request body cho `/move` endpoint.
    
    Attributes:
        board_state (List[List[int]]): Mảng 10x9 đại diện cho bàn cờ.
        is_red_turn (bool): True nếu là lượt Đỏ, False nếu là lượt Đen.
        half_move_clock (int): Số nửa nước đi (cho luật hòa 120 nước).
        history (List[str]): Lịch sử các mã băm bàn cờ để kiểm tra lặp 3 lần.
    """
    board_state: List[List[int]]  # Mảng 10x9
    is_red_turn: bool  # True = lượt Đỏ
    half_move_clock: int = 0
    history: List[str] = []


class MoveResponse(BaseModel):
    """Response trả về từ `/move` endpoint.
    
    Attributes:
        from_row (int): Hàng bắt đầu của nước đi.
        from_col (int): Cột bắt đầu của nước đi.
        to_row (int): Hàng đích đến của nước đi.
        to_col (int): Cột đích đến của nước đi.
        score (int): Điểm số đánh giá cho nước đi này.
        half_move_clock (int): Giá trị clock sau khi đi (cập nhật).
        history (List[str]): Lịch sử cập nhật sau khi thực hiện nước đi.
    """
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    score: int
    half_move_clock: int
    history: List[str]


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
    """Kiểm tra trạng thái hoạt động của API server.
    
    Returns:
        dict: Một dictionary chứa trạng thái hệ thống, ví dụ `{"status": "ok"}`.
    """
    return {"status": "ok"}


@app.post("/move", response_model=MoveResponse)
def get_ai_move(request: MoveRequest):
    """Endpoint chính cho AI tính toán nước đi tốt nhất.
    
    Dựa trên cấu hình bàn cờ hiện tại, endpoint sẽ sinh ra nước đi tiếp theo
    sử dụng thuật toán Minimax và Alpha-Beta pruning thông qua `AIEngine`.
    
    Args:
        request (MoveRequest): Đối tượng chứa trạng thái hiện tại của bàn cờ và lượt đi.
    
    Returns:
        MoveResponse: Tọa độ nước đi tốt nhất, điểm số đánh giá, cùng trạng thái clock và history mới.
        
    Raises:
        Exception: Nếu không tìm thấy nước đi nào hợp lệ.
    """
    # Tạo Board từ board_state
    board = Board()
    board.board = request.board_state
    board.half_move_clock = request.half_move_clock
    board.history = request.history

    # Tạo AIEngine và tìm nước đi tốt nhất
    engine = AIEngine(board, max_depth=5, time_limit=0.5)
    best_move = engine.get_best_move(request.is_red_turn)
    
    if best_move is None:
        raise Exception("Không có nước đi hợp lệ")
    
    from_row, from_col, to_row, to_col = best_move
    move_gen = MoveGenerator(board)
    if (to_row, to_col) not in move_gen.generate_moves(from_row, from_col):
        raise Exception(f"AI trả về nước đi không hợp lệ: {best_move}")
    
    # Thực hiện nước đi trên board để lấy clock và history mới
    board.move_piece(from_row, from_col, to_row, to_col)
    
    # Tính điểm số hiện tại
    evaluator = Evaluator(board)
    score = evaluator.evaluate()
    
    return MoveResponse(
        from_row=from_row,
        from_col=from_col,
        to_row=to_row,
        to_col=to_col,
        score=score,
        half_move_clock=board.half_move_clock,
        history=board.history
    )


# Chạy server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
