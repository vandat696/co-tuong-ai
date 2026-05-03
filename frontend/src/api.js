import axios from "axios";

// Địa chỉ của Backend FastAPI
const API_URL = "http://localhost:8000";

/**
 * Gọi API yêu cầu AI tính toán nước đi tiếp theo
 *
 * @param {Array<Array<number>>} boardState - Ma trận 10x9 chứa các số nguyên đại diện cho quân cờ
 * @param {boolean} isRedTurn - True nếu AI cầm cờ Đỏ, False nếu AI cầm cờ Đen
 * @returns {Promise<Object>} - Object chứa tọa độ nước đi: {from_row, from_col, to_row, to_col, score}
 */
export const fetchAIMove = async (boardState, isRedTurn) => {
  try {
    const response = await axios.post(`${API_URL}/move`, {
      // Tên biến gửi đi phải khớp với cấu trúc MoveRequest (Pydantic model) trong backend/api.py
      board_state: boardState,
      is_red_turn: isRedTurn,
    });

    return response.data;
  } catch (error) {
    console.error("Lỗi khi kết nối với AI Backend:", error);
    throw error;
  }
};
