import axios from "axios";

const API_URL = "http://localhost:8000";

export const fetchAIVersions = async () => {
  const response = await axios.get(`${API_URL}/ai-versions`);
  return response.data;
};

export const fetchAIMove = async ({
  boardState,
  isRedTurn,
  aiVersion,
  halfMoveClock = 0,
  history = [],
}) => {
  const response = await axios.post(`${API_URL}/move`, {
    board_state: boardState,
    is_red_turn: isRedTurn,
    ai_version: aiVersion,
    half_move_clock: halfMoveClock,
    history,
  });

  return response.data;
};
