import React from "react";
import { useGame } from "../hooks/useGame";
import Piece from "./Piece";
import "./Board.css";

const Board = () => {
  // Game state management
  const {
    board,
    selectedPos,
    validMoves,
    currentPlayer,
    lastAIMove,
    handlePieceClick,
    resetGame,
  } = useGame();

  // Kích thước ô (pixels giữa các giao điểm)
  const CELL_SIZE = 60;
  const PADDING = 40; // Lề ngoài của bàn
  const BOARD_WIDTH = 8 * CELL_SIZE + PADDING * 2; // 9 cột
  const BOARD_HEIGHT = 9 * CELL_SIZE + PADDING * 2; // 10 hàng

  // Hàm tính vị trí của giao điểm (row, col)
  const getPositionByGrid = (row, col) => ({
    x: PADDING + col * CELL_SIZE,
    y: PADDING + row * CELL_SIZE,
  });

  // Lấy danh sách quân cờ dạng mảng phẳng và giữ thứ tự cố định theo ID.
  // Kỹ thuật này giúp các node SVG không bị thay đổi thứ tự trong DOM khi bàn cờ cập nhật,
  // từ đó CSS Transition được kích hoạt hoàn hảo 100% mượt mà.
  const activePieces = [];
  board.forEach((row, rowIndex) => {
    row.forEach((piece, colIndex) => {
      if (piece) {
        activePieces.push({ ...piece, rowIndex, colIndex });
      }
    });
  });
  activePieces.sort((a, b) => {
    const idA = parseInt(a.id.split("-")[1]);
    const idB = parseInt(b.id.split("-")[1]);
    return idA - idB;
  });

  return (
    <div className="board-container">
      <div className="board-wrapper">
        {/* Thêm CSS để tạo hiệu ứng lướt mượt mà cho quân cờ */}
        <style>{`
          .piece-wrapper {
            transition: transform 0.4s cubic-bezier(0.25, 0.1, 0.25, 1);
          }
        `}</style>

        {/* SVG vẽ lưới bàn cờ */}
        <svg
          className="board-svg"
          width={BOARD_WIDTH}
          height={BOARD_HEIGHT}
          style={{ border: "2px solid #8b4513" }}
        >
          {/* Vẽ các đường kẻ ngang */}
          {Array(10)
            .fill(null)
            .map((_, i) => (
              <line
                key={`h-${i}`}
                x1={PADDING}
                y1={PADDING + i * CELL_SIZE}
                x2={PADDING + 8 * CELL_SIZE}
                y2={PADDING + i * CELL_SIZE}
                stroke="#000"
                strokeWidth="1"
              />
            ))}

          {/* Vẽ 2 đường dọc ngoài cùng (xuyên qua sông) */}
          <line
            x1={PADDING}
            y1={PADDING}
            x2={PADDING}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
          />
          <line
            x1={PADDING + 8 * CELL_SIZE}
            y1={PADDING}
            x2={PADDING + 8 * CELL_SIZE}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
          />

          {/* Vẽ 7 đường dọc giữa - chỉ trên và dưới sông */}
          {Array(7)
            .fill(null)
            .map((_, i) => {
              const colIndex = i + 1; // Cột 1-7
              return (
                <g key={`v-middle-${i}`}>
                  <line
                    x1={PADDING + colIndex * CELL_SIZE}
                    y1={PADDING}
                    x2={PADDING + colIndex * CELL_SIZE}
                    y2={PADDING + 4 * CELL_SIZE}
                    stroke="#000"
                    strokeWidth="1"
                  />
                  <line
                    x1={PADDING + colIndex * CELL_SIZE}
                    y1={PADDING + 5 * CELL_SIZE}
                    x2={PADDING + colIndex * CELL_SIZE}
                    y2={PADDING + 9 * CELL_SIZE}
                    stroke="#000"
                    strokeWidth="1"
                  />
                </g>
              );
            })}

          {/* Vẽ sông (River) - dòng chữ */}
          <text
            x={PADDING + 2 * CELL_SIZE}
            y={PADDING + 4.5 * CELL_SIZE + 8}
            fontSize="18"
            fontWeight="bold"
            fill="#666"
            textAnchor="middle"
          >
            楚河
          </text>
          <text
            x={PADDING + 6 * CELL_SIZE}
            y={PADDING + 4.5 * CELL_SIZE + 8}
            fontSize="18"
            fontWeight="bold"
            fill="#666"
            textAnchor="middle"
          >
            漢界
          </text>

          {/* Vẽ cung tướng Đỏ (ví dụ - 3x3 ở góc trên) */}
          <line
            x1={PADDING + 3 * CELL_SIZE}
            y1={PADDING}
            x2={PADDING + 5 * CELL_SIZE}
            y2={PADDING + 2 * CELL_SIZE}
            stroke="#f00"
            strokeWidth="1"
            opacity="0.5"
          />
          <line
            x1={PADDING + 5 * CELL_SIZE}
            y1={PADDING}
            x2={PADDING + 3 * CELL_SIZE}
            y2={PADDING + 2 * CELL_SIZE}
            stroke="#f00"
            strokeWidth="1"
            opacity="0.5"
          />

          {/* Vẽ cung tướng Đen (3x3 ở góc dưới) */}
          <line
            x1={PADDING + 3 * CELL_SIZE}
            y1={PADDING + 7 * CELL_SIZE}
            x2={PADDING + 5 * CELL_SIZE}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
            opacity="0.5"
          />
          <line
            x1={PADDING + 5 * CELL_SIZE}
            y1={PADDING + 7 * CELL_SIZE}
            x2={PADDING + 3 * CELL_SIZE}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
            opacity="0.5"
          />

          {/* Hiển thị vị trí hợp lệ của người chơi */}
          {validMoves.map(([row, col], idx) => {
            const pos = getPositionByGrid(row, col);
            return (
              <circle
                key={`valid-${idx}`}
                cx={pos.x}
                cy={pos.y}
                r="15"
                fill="#00ff00"
                opacity="0.6"
                onClick={() => handlePieceClick(row, col)}
                style={{ cursor: "pointer" }}
              />
            );
          })}

          {/* Hiệu ứng nước đi cuối của AI - cùng hình dạng với marker của người chơi, chỉ khác màu */}
          {lastAIMove &&
            (() => {
              const fromPos = getPositionByGrid(
                lastAIMove.from[0],
                lastAIMove.from[1],
              );
              const toPos = getPositionByGrid(
                lastAIMove.to[0],
                lastAIMove.to[1],
              );

              return (
                <g className="ai-last-move-indicator">
                  {/* Chấm ở vị trí cũ */}
                  <circle
                    cx={fromPos.x}
                    cy={fromPos.y}
                    r="15"
                    fill="#3399ff"
                    opacity="0.7"
                  />
                </g>
              );
            })()}

          {/* Hiển thị các quân cờ */}
          {activePieces.map((piece) => {
            const pos = getPositionByGrid(piece.rowIndex, piece.colIndex);
            const isSelected =
              selectedPos &&
              selectedPos[0] === piece.rowIndex &&
              selectedPos[1] === piece.colIndex;

            const isAiLastMoveTarget =
              lastAIMove &&
              lastAIMove.to[0] === piece.rowIndex &&
              lastAIMove.to[1] === piece.colIndex;

            return (
              <g
                key={piece.id}
                className="piece-wrapper"
                onClick={() => handlePieceClick(piece.rowIndex, piece.colIndex)}
                style={{
                  cursor: "pointer",
                  transform: `translate(${pos.x}px, ${pos.y}px)`,
                }}
              >
                <Piece
                  type={piece.type}
                  side={piece.side}
                  x={0}
                  y={0}
                  isSelected={isSelected}
                  isAiLastMoveTarget={isAiLastMoveTarget}
                />
              </g>
            );
          })}
        </svg>

        {/* Game info */}
        <div className="game-info">
          <div className="player-info">
            <span className={`player ${currentPlayer}`}>
              {currentPlayer === "red" ? "🔴 Red" : "⚫ Black"} Player
            </span>
          </div>
          <button className="reset-btn" onClick={resetGame}>
            ↻ Reset Game
          </button>
        </div>
      </div>
    </div>
  );
};

export default Board;