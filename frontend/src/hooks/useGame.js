import { useState, useCallback, useEffect } from "react";
import { fetchAIMove } from "../api";

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
    (row, col, piece) => {
      const moves = [];
      const { type, side } = piece;

      // Direction helpers
      const isInBounds = (r, c) => r >= 0 && r < 10 && c >= 0 && c < 9;
      const isEmpty = (r, c) => board[r][c] === null;
      const isEnemy = (r, c) => board[r][c] && board[r][c].side !== side;

      // Palace boundaries
      const isInPalace = (r, c, s) => {
        if (s === "red") return r >= 7 && r <= 9 && c >= 3 && c <= 5;
        return r >= 0 && r <= 2 && c >= 3 && c <= 5;
      };

      if (type === "chariot") {
        // Chariot moves in straight lines (no obstacles)
        const directions = [
          [0, 1],
          [0, -1],
          [1, 0],
          [-1, 0],
        ];
        for (const [dr, dc] of directions) {
          let nr = row + dr,
            nc = col + dc;
          while (isInBounds(nr, nc)) {
            if (isEmpty(nr, nc)) {
              moves.push([nr, nc]);
            } else if (isEnemy(nr, nc)) {
              moves.push([nr, nc]);
              break;
            } else {
              break;
            }
            nr += dr;
            nc += dc;
          }
        }
      } else if (type === "horse") {
        // Horse moves in L-shape but blocked by adjacent pieces
        const jumps = [
          [
            [-1, 0],
            [-2, -1],
          ],
          [
            [-1, 0],
            [-2, 1],
          ],
          [
            [0, -1],
            [-1, -2],
          ],
          [
            [0, -1],
            [1, -2],
          ],
          [
            [0, 1],
            [-1, 2],
          ],
          [
            [0, 1],
            [1, 2],
          ],
          [
            [1, 0],
            [2, -1],
          ],
          [
            [1, 0],
            [2, 1],
          ],
        ];

        for (const [adj, target] of jumps) {
          const adjR = row + adj[0],
            adjC = col + adj[1];
          const tarR = row + target[0],
            tarC = col + target[1];

          if (
            isInBounds(adjR, adjC) &&
            isEmpty(adjR, adjC) &&
            isInBounds(tarR, tarC) &&
            (isEmpty(tarR, tarC) || isEnemy(tarR, tarC))
          ) {
            moves.push([tarR, tarC]);
          }
        }
      } else if (type === "elephant") {
        // Elephant moves diagonally 2 steps, not crossing river, blocked by adjacent piece
        const jumps = [
          [-2, -2],
          [-2, 2],
          [2, -2],
          [2, 2],
        ];
        for (const [dr, dc] of jumps) {
          const adjR = row + dr / 2,
            adjC = col + dc / 2;
          const tarR = row + dr,
            tarC = col + dc;

          if (
            isInBounds(tarR, tarC) &&
            isEmpty(adjR, adjC) &&
            (isEmpty(tarR, tarC) || isEnemy(tarR, tarC))
          ) {
            // Elephant doesn't cross river
            if (side === "red" && tarR <= 9 && tarR >= 5) {
              moves.push([tarR, tarC]);
            } else if (side === "black" && tarR >= 0 && tarR <= 4) {
              moves.push([tarR, tarC]);
            }
          }
        }
      } else if (type === "advisor") {
        // Advisor moves 1 step diagonally, stays in palace
        const jumps = [
          [-1, -1],
          [-1, 1],
          [1, -1],
          [1, 1],
        ];
        for (const [dr, dc] of jumps) {
          const nr = row + dr,
            nc = col + dc;
          if (
            isInBounds(nr, nc) &&
            isInPalace(nr, nc, side) &&
            (isEmpty(nr, nc) || isEnemy(nr, nc))
          ) {
            moves.push([nr, nc]);
          }
        }
      } else if (type === "general") {
        // General moves 1 step orthogonally, stays in palace
        const directions = [
          [0, 1],
          [0, -1],
          [1, 0],
          [-1, 0],
        ];
        for (const [dr, dc] of directions) {
          const nr = row + dr,
            nc = col + dc;
          if (
            isInBounds(nr, nc) &&
            isInPalace(nr, nc, side) &&
            (isEmpty(nr, nc) || isEnemy(nr, nc))
          ) {
            moves.push([nr, nc]);
          }
        }
      } else if (type === "cannon") {
        // Cannon moves like chariot but must jump over 1 piece to capture
        const directions = [
          [0, 1],
          [0, -1],
          [1, 0],
          [-1, 0],
        ];
        for (const [dr, dc] of directions) {
          // Move without capturing
          let nr = row + dr,
            nc = col + dc;
          while (isInBounds(nr, nc) && isEmpty(nr, nc)) {
            moves.push([nr, nc]);
            nr += dr;
            nc += dc;
          }

          // Jump over one piece to capture
          if (isInBounds(nr, nc) && !isEmpty(nr, nc)) {
            nr += dr;
            nc += dc;
            while (isInBounds(nr, nc)) {
              if (isEmpty(nr, nc)) {
                nr += dr;
                nc += dc;
              } else if (isEnemy(nr, nc)) {
                moves.push([nr, nc]);
                break;
              } else {
                break;
              }
            }
          }
        }
      } else if (type === "pawn") {
        // Pawn before crossing river can move forward only
        // After crossing river can move forward or sideways
        const isCrossedRiver =
          (side === "red" && row < 5) || (side === "black" && row > 4);

        if (side === "red") {
          // Forward
          if (row > 0 && (isEmpty(row - 1, col) || isEnemy(row - 1, col))) {
            moves.push([row - 1, col]);
          }
          if (isCrossedRiver) {
            // Sideways
            if (col > 0 && (isEmpty(row, col - 1) || isEnemy(row, col - 1))) {
              moves.push([row, col - 1]);
            }
            if (col < 8 && (isEmpty(row, col + 1) || isEnemy(row, col + 1))) {
              moves.push([row, col + 1]);
            }
          }
        } else {
          // Forward (for black, downward)
          if (row < 9 && (isEmpty(row + 1, col) || isEnemy(row + 1, col))) {
            moves.push([row + 1, col]);
          }
          if (isCrossedRiver) {
            // Sideways
            if (col > 0 && (isEmpty(row, col - 1) || isEnemy(row, col - 1))) {
              moves.push([row, col - 1]);
            }
            if (col < 8 && (isEmpty(row, col + 1) || isEnemy(row, col + 1))) {
              moves.push([row, col + 1]);
            }
          }
        }
      }

      // === LỌC LUẬT CHỐNG TƯỚNG (FLYING GENERAL) ===
      const isKingsFacing = (tempBoard) => {
        let redKing = null;
        let blackKing = null;

        for (let r = 0; r < 10; r++) {
          for (let c = 0; c < 9; c++) {
            const p = tempBoard[r][c];
            if (p && p.type === "king") {
              if (p.side === "red") redKing = [r, c];
              else blackKing = [r, c];
            }
          }
        }

        if (!redKing || !blackKing) return false;
        if (redKing[1] !== blackKing[1]) return false; // Khác cột

        const col = redKing[1];
        const startRow = Math.min(redKing[0], blackKing[0]);
        const endRow = Math.max(redKing[0], blackKing[0]);

        for (let r = startRow + 1; r < endRow; r++) {
          if (tempBoard[r][col] !== null) return false; // Có quân cản ở giữa
        }
        return true;
      };

      return moves.filter(([tarR, tarC]) => {
        const tempBoard = board.map((r) => [...r]);
        tempBoard[tarR][tarC] = piece;
        tempBoard[row][col] = null;
        return !isKingsFacing(tempBoard);
      });
    },
    [board],
  );

  // Handle piece click
  const handlePieceClick = useCallback(
    (row, col) => {
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
        const fromPiece = board[fromRow][fromCol];

        // Check if target is in valid moves
        const isValidMove = validMoves.some(([r, c]) => r === row && c === col);

        if (isValidMove) {
          // Make the move
          const newBoard = board.map((r) => [...r]);
          newBoard[row][col] = fromPiece;
          newBoard[fromRow][fromCol] = null;
          setBoard(newBoard);

          // Xóa dấu nước đi AI cũ khi người chơi đã đi tiếp
          setLastAIMove(null);

          // Switch player
          setCurrentPlayer(currentPlayer === "red" ? "black" : "red");
          setSelectedPos(null);
          setValidMoves([]);
        } else {
          // Select new piece if it's your turn
          if (piece && piece.side === currentPlayer) {
            setSelectedPos([row, col]);
            setValidMoves(calculateValidMoves(row, col, piece));
          } else {
            setSelectedPos(null);
            setValidMoves([]);
          }
        }
      } else if (piece && piece.side === currentPlayer) {
        // Select a piece
        setSelectedPos([row, col]);
        setValidMoves(calculateValidMoves(row, col, piece));
      }
    },
    [board, selectedPos, validMoves, currentPlayer, calculateValidMoves],
  );

  // Lắng nghe sự thay đổi lượt chơi, nếu đến lượt Đen (AI) thì tự động gọi API
  useEffect(() => {
    if (currentPlayer === "black") {
      const playAIMove = async () => {
        try {
          // 1. Chuyển đổi dữ liệu bàn cờ
          const intBoard = boardToIntArray(board);

          // 2. Gọi API lấy nước đi từ AI
          const aiMove = await fetchAIMove(intBoard, false); // false = AI cầm cờ Đen
          const { from_row, from_col, to_row, to_col } = aiMove;

          // Thêm một độ trễ nhỏ để tạo cảm giác AI đang "suy nghĩ"
          await new Promise((resolve) => setTimeout(resolve, 600));

          // 3. Cập nhật bàn cờ với nước đi của AI
          setBoard((prevBoard) => {
            const newBoard = prevBoard.map((r) => [...r]);
            newBoard[to_row][to_col] = newBoard[from_row][from_col];
            newBoard[from_row][from_col] = null;
            return newBoard;
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
        }
      };

      playAIMove();
    }
  }, [currentPlayer]);

  return {
    board,
    selectedPos,
    validMoves,
    currentPlayer,
    lastAIMove,
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
