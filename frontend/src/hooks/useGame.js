import { useState, useCallback, useEffect, useMemo } from "react";
import { fetchAIMove } from "../api";
import { XiangqiRules } from "../game/XiangqiRules";

// Co-tuong (Chinese Chess) piece setup
// Board is 10 rows x 9 columns
// Red pieces start at bottom (rows 7-9), Black pieces at top (rows 0-2)

const INITIAL_BOARD = () => {
  const board = Array(10)
    .fill(null)
    .map(() => Array(9).fill(null));

  // Red pieces setup (bottom)
  // Row 9: Chariots, Horses, Advisors, Elephants, General
  board[9][0] = { type: "chariot", side: "red" };
  board[9][1] = { type: "horse", side: "red" };
  board[9][2] = { type: "elephant", side: "red" };
  board[9][3] = { type: "advisor", side: "red" };
  board[9][4] = { type: "king", side: "red" };
  board[9][5] = { type: "advisor", side: "red" };
  board[9][6] = { type: "elephant", side: "red" };
  board[9][7] = { type: "horse", side: "red" };
  board[9][8] = { type: "chariot", side: "red" };

  // Row 7: Cannons
  board[7][1] = { type: "cannon", side: "red" };
  board[7][7] = { type: "cannon", side: "red" };

  // Row 6: Pawns
  board[6][0] = { type: "pawn", side: "red" };
  board[6][2] = { type: "pawn", side: "red" };
  board[6][4] = { type: "pawn", side: "red" };
  board[6][6] = { type: "pawn", side: "red" };
  board[6][8] = { type: "pawn", side: "red" };

  // Black pieces setup (top)
  // Row 0: Chariots, Horses, Advisors, Elephants, General
  board[0][0] = { type: "chariot", side: "black" };
  board[0][1] = { type: "horse", side: "black" };
  board[0][2] = { type: "elephant", side: "black" };
  board[0][3] = { type: "advisor", side: "black" };
  board[0][4] = { type: "king", side: "black" };
  board[0][5] = { type: "advisor", side: "black" };
  board[0][6] = { type: "elephant", side: "black" };
  board[0][7] = { type: "horse", side: "black" };
  board[0][8] = { type: "chariot", side: "black" };

  // Row 2: Cannons
  board[2][1] = { type: "cannon", side: "black" };
  board[2][7] = { type: "cannon", side: "black" };

  // Row 3: Pawns
  board[3][0] = { type: "pawn", side: "black" };
  board[3][2] = { type: "pawn", side: "black" };
  board[3][4] = { type: "pawn", side: "black" };
  board[3][6] = { type: "pawn", side: "black" };
  board[3][8] = { type: "pawn", side: "black" };

  // Gắn ID duy nhất cho mỗi quân cờ để React có thể animate khi di chuyển
  let idCounter = 0;
  for (let r = 0; r < 10; r++) {
    for (let c = 0; c < 9; c++) {
      if (board[r][c]) {
        board[r][c].id = `piece-${idCounter++}`;
      }
    }
  }

  return board;
};

// Helper chuyển đổi bàn cờ Frontend (Object) sang Backend (Integer array)
const boardToIntArray = (board) => {
  const typeMap = {
    king: 1,
    advisor: 2,
    elephant: 3,
    chariot: 4,
    horse: 5,
    cannon: 6,
    pawn: 7,
  };

  return board.map((row) =>
    row.map((piece) => {
      if (!piece) return 0;
      const val = typeMap[piece.type];
      return piece.side === "red" ? val : -val;
    }),
  );
};

export const useGame = () => {
  const [board, setBoard] = useState(INITIAL_BOARD());
  const [selectedPos, setSelectedPos] = useState(null);
  const [validMoves, setValidMoves] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState("red");
  const [lastAIMove, setLastAIMove] = useState(null);

  // Calculate valid moves for a piece
  const calculateValidMoves = useCallback(
    (row, col) => XiangqiRules.getLegalMoves(board, row, col),
    [board],
  );

  const gameStatus = useMemo(() => {
    return XiangqiRules.getGameStatus(board, currentPlayer);
  }, [board, currentPlayer]);

  // Handle piece click
  const handlePieceClick = useCallback(
    (row, col) => {
      if (gameStatus.isCheckmate) return;

      const piece = board[row][col];

      // If clicking the same piece, deselect it
      if (selectedPos && selectedPos[0] === row && selectedPos[1] === col) {
        setSelectedPos(null);
        setValidMoves([]);
        return;
      }

      // If clicking empty space or opponent piece, try to move
      if (selectedPos) {
        const [fromRow, fromCol] = selectedPos;

        // Check if target is in valid moves
        const isValidMove = validMoves.some(([r, c]) => r === row && c === col);

        if (isValidMove) {
          // Make the move
          const newBoard = XiangqiRules.applyMove(board, fromRow, fromCol, row, col);
          setBoard(newBoard);

          // Xóa dấu nước đi AI cũ khi người chơi đã đi tiếp
          setLastAIMove(null);

          // Switch player
          setCurrentPlayer(XiangqiRules.getOpponent(currentPlayer));
          setSelectedPos(null);
          setValidMoves([]);
        } else {
          // Select new piece if it's your turn
          if (piece && piece.side === currentPlayer) {
            setSelectedPos([row, col]);
            setValidMoves(calculateValidMoves(row, col));
          } else {
            setSelectedPos(null);
            setValidMoves([]);
          }
        }
      } else if (piece && piece.side === currentPlayer) {
        // Select a piece
        setSelectedPos([row, col]);
        setValidMoves(calculateValidMoves(row, col));
      }
    },
    [board, selectedPos, validMoves, currentPlayer, calculateValidMoves, gameStatus.isCheckmate],
  );

  // Lắng nghe sự thay đổi lượt chơi, nếu đến lượt Đen (AI) thì tự động gọi API
  useEffect(() => {
    if (currentPlayer === "black" && !gameStatus.isCheckmate) {
      const playAIMove = async () => {
        try {
          // 1. Chuyển đổi dữ liệu bàn cờ
          const intBoard = boardToIntArray(board);

          // 2. Gọi API lấy nước đi từ AI
          let aiMove = await fetchAIMove(intBoard, false); // false = AI cầm cờ Đen

          const isLegalMove = (move) =>
            XiangqiRules.isLegalMove(
              board,
              move.from_row,
              move.from_col,
              move.to_row,
              move.to_col,
              "black",
            );

          if (!aiMove || !isLegalMove(aiMove)) {
            console.warn("AI trả về nước đi không hợp lệ, dùng nước dự phòng:", aiMove);
            aiMove = XiangqiRules.getFallbackMove(board, "black");
          }

          if (!aiMove) {
            throw new Error("AI không có nước đi hợp lệ");
          }

          const { from_row, from_col, to_row, to_col } = aiMove;

          // Thêm một độ trễ nhỏ để tạo cảm giác AI đang "suy nghĩ"
          await new Promise((resolve) => setTimeout(resolve, 600));

          // 3. Cập nhật bàn cờ với nước đi của AI
          setBoard((prevBoard) => {
            const isLegalAIMove = XiangqiRules.isLegalMove(
              prevBoard,
              from_row,
              from_col,
              to_row,
              to_col,
              "black",
            );

            if (!isLegalAIMove) {
              console.error("AI trả về nước đi không hợp lệ:", aiMove);
              return prevBoard;
            }

            return XiangqiRules.applyMove(prevBoard, from_row, from_col, to_row, to_col);
          });

          // 4. Lưu nước đi cuối của AI để render hiệu ứng
          setLastAIMove({
            from: [from_row, from_col],
            to: [to_row, to_col],
            side: "black",
          });

          // 5. Chuyển lại lượt cho người (Đỏ)
          setCurrentPlayer("red");
        } catch (error) {
          console.error("Lỗi khi AI đánh:", error);
          setCurrentPlayer("red");
        }
      };

      playAIMove();
    }
  }, [currentPlayer, board, gameStatus.isCheckmate]);

  return {
    board,
    selectedPos,
    validMoves,
    currentPlayer,
    lastAIMove,
    gameStatus,
    handlePieceClick,
    resetGame: () => {
      setBoard(INITIAL_BOARD());
      setSelectedPos(null);
      setValidMoves([]);
      setCurrentPlayer("red");
      setLastAIMove(null);
    },
  };
};
