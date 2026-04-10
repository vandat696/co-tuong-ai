/**
 * api.js - Frontend API service for co-tuong game
 * Handles communication with the Python FastAPI backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Piece encoding for backend
 * Red: positive numbers, Black: negative numbers
 * 1: Chariot, 2: Horse, 3: Elephant, 4: Advisor, 5: General, 6: Cannon, 7: Pawn
 */
const PIECE_ENCODING = {
  chariot: 1,
  horse: 2,
  elephant: 3,
  advisor: 4,
  general: 5,
  king: 5, // king is same as general
  cannon: 6,
  pawn: 7,
};

const PIECE_DECODING = {
  1: 'chariot',
  2: 'horse',
  3: 'elephant',
  4: 'advisor',
  5: 'general',
  6: 'cannon',
  7: 'pawn',
};

/**
 * Validate board state format
 * @param {Array} boardState - Board state to validate
 * @returns {boolean} True if valid
 */
const validateBoardState = (boardState) => {
  if (!Array.isArray(boardState) || boardState.length !== 10) {
    console.error(`Invalid board rows: expected 10, got ${boardState?.length}`);
    return false;
  }
  
  for (let i = 0; i < boardState.length; i++) {
    if (!Array.isArray(boardState[i]) || boardState[i].length !== 9) {
      console.error(`Invalid board cols at row ${i}: expected 9, got ${boardState[i]?.length}`);
      return false;
    }
    for (let j = 0; j < boardState[i].length; j++) {
      const val = boardState[i][j];
      if (typeof val !== 'number' || !Number.isInteger(val)) {
        console.error(`Invalid value at [${i}, ${j}]: expected integer, got ${typeof val} = ${val}`);
        return false;
      }
    }
  }
  return true;
};

/**
 * Convert frontend board format to backend board_state (10x9 with encoded integers)
 * @param {Array} board - Frontend board format (10x9 with {type, side} or null)
 * @returns {Array} Backend board_state (10x9 with encoded integers)
 */
export const encodeBoardState = (board) => {
  return board.map((row, rowIdx) =>
    row.map((piece, colIdx) => {
      if (!piece) return 0;
      const pieceCode = PIECE_ENCODING[piece.type];
      if (pieceCode === undefined) {
        console.warn(`Unknown piece type at [${rowIdx}, ${colIdx}]: ${piece.type}`);
        return 0;
      }
      return piece.side === 'red' ? pieceCode : -pieceCode;
    })
  );
};

/**
 * Convert backend board_state to frontend board format
 * @param {Array} boardState - Backend board_state (10x9 with encoded integers)
 * @returns {Array} Frontend board format (10x9 with {type, side} or null)
 */
export const decodeBoardState = (boardState) => {
  if (!validateBoardState(boardState)) {
    console.error('Invalid board state format');
    return null;
  }
  

  return boardState.map((row) =>
    row.map((code) => {
      if (code === 0) return null;
      const absCode = Math.abs(code);
      const type = PIECE_DECODING[absCode];
      const side = code > 0 ? 'red' : 'black';
      return { type, side };
    })
  );
};

/**
 * Call AI to get the best move
 * @param {Array} board - Current board state (frontend format)
 * @param {boolean} isRedTurn - True if it's red's turn
 * @returns {Promise} Response with move details {from_row, from_col, to_row, to_col, score}
 */
export const getMoveFromAI = async (board, isRedTurn) => {
  try {
    const boardState = encodeBoardState(board);
    
    // Validate board state before sending
    if (!validateBoardState(boardState)) {
      throw new Error('Invalid board state format - see console for details');
    }

    console.log('Sending move request to AI:');
    console.log(`  - Board size: ${boardState.length}x${boardState[0].length}`);
    console.log(`  - Red's turn: ${isRedTurn}`);
    console.log(`  - Board state:`, boardState);

    const response = await fetch(`${API_BASE_URL}/move`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        board_state: boardState,
        is_red_turn: isRedTurn,
      }),
    });

    if (!response.ok) {
      let errorMsg = `API error: ${response.status}`;
      try {
        const errorData = await response.json();
        console.error('API validation error:', errorData);
        errorMsg = errorData.detail || JSON.stringify(errorData);
      } catch (e) {
        const text = await response.text();
        console.error('API error response:', text);
        errorMsg = text || errorMsg;
      }
      throw new Error(errorMsg);
    }

    const result = await response.json();
    console.log('AI move result:', result);
    return {
      from: [result.from_row, result.from_col],
      to: [result.to_row, result.to_col],
      score: result.score,
    };
  } catch (error) {
    console.error('Error calling AI move API:', error);
    throw error;
  }
};

/**
 * Health check - verify API connection
 * @returns {Promise} Response with status
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

export default {
  getMoveFromAI,
  healthCheck,
  encodeBoardState,
  decodeBoardState,
};
