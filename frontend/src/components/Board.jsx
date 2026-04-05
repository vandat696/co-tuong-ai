import React from 'react';
import { useGame } from '../hooks/useGame';
import Piece from './Piece';
import './Board.css';

const Board = () => {
  // Game state management
  const { board, selectedPos, validMoves, currentPlayer, handlePieceClick, resetGame } = useGame();

  // Kích thước ô (pixels giữa các giao điểm)
  const CELL_SIZE = 60;
  const PADDING = 40; // Lề ngoài của bàn
  const BOARD_WIDTH = 8 * CELL_SIZE + PADDING * 2;  // 9 cột
  const BOARD_HEIGHT = 9 * CELL_SIZE + PADDING * 2; // 10 hàng

  // Hàm tính vị trí của giao điểm (row, col)
  const getPositionByGrid = (row, col) => ({
    x: PADDING + col * CELL_SIZE,
    y: PADDING + row * CELL_SIZE
  });

  return (
    <div className="board-container">
      <div className="board-wrapper">
        {/* SVG vẽ lưới bàn cờ */}
        <svg 
          className="board-svg" 
          width={BOARD_WIDTH} 
          height={BOARD_HEIGHT}
          style={{ border: '2px solid #8b4513' }}
        >
          {/* Vẽ các đường kẻ ngang */}
          {Array(10).fill(null).map((_, i) => (
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
        <line x1={PADDING} y1={PADDING} x2={PADDING} y2={PADDING + 9 * CELL_SIZE} stroke="#000" strokeWidth="1" />
        <line x1={PADDING + 8 * CELL_SIZE} y1={PADDING} x2={PADDING + 8 * CELL_SIZE} y2={PADDING + 9 * CELL_SIZE} stroke="#000" strokeWidth="1" />
        
        {/* Vẽ 7 đường dọc giữa - chỉ trên và dưới sông */}
        {Array(7).fill(null).map((_, i) => {
          const colIndex = i + 1; // Cột 1-7
          return (
            <g key={`v-middle-${i}`}>
              <line x1={PADDING + colIndex * CELL_SIZE} y1={PADDING} x2={PADDING + colIndex * CELL_SIZE} y2={PADDING + 4 * CELL_SIZE} stroke="#000" strokeWidth="1" />
              <line x1={PADDING + colIndex * CELL_SIZE} y1={PADDING + 5 * CELL_SIZE} x2={PADDING + colIndex * CELL_SIZE} y2={PADDING + 9 * CELL_SIZE} stroke="#000" strokeWidth="1" />
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
          {/* Đường chéo thứ nhất */}
          <line
            x1={PADDING + 3 * CELL_SIZE}
            y1={PADDING}
            x2={PADDING + 5 * CELL_SIZE}
            y2={PADDING + 2 * CELL_SIZE}
            stroke="#f00"
            strokeWidth="1"
            opacity="0.5"
          />
          {/* Đường chéo thứ hai */}
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
          {/* Đường chéo thứ nhất */}
          <line
            x1={PADDING + 3 * CELL_SIZE}
            y1={PADDING + 7 * CELL_SIZE}
            x2={PADDING + 5 * CELL_SIZE}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
            opacity="0.5"
          />
          {/* Đường chéo thứ hai */}
          <line
            x1={PADDING + 5 * CELL_SIZE}
            y1={PADDING + 7 * CELL_SIZE}
            x2={PADDING + 3 * CELL_SIZE}
            y2={PADDING + 9 * CELL_SIZE}
            stroke="#000"
            strokeWidth="1"
            opacity="0.5"
          />

          {/* Hiển thị vị trí hợp lệ */}
          {validMoves.map(([row, col], idx) => {
            const pos = getPositionByGrid(row, col);
            return (
              <circle
                key={`valid-${idx}`}
                cx={pos.x}
                cy={pos.y}
                r="8"
                fill="#00ff00"
                opacity="0.6"
              />
            );
          })}

          {/* Hiển thị các quân cờ */}
          {board.map((row, rowIndex) =>
            row.map((piece, colIndex) => {
              if (!piece) return null;
              const pos = getPositionByGrid(rowIndex, colIndex);
              const isSelected = selectedPos && selectedPos[0] === rowIndex && selectedPos[1] === colIndex;
              
              return (
                <g
                  key={`piece-${rowIndex}-${colIndex}`}
                  onClick={() => handlePieceClick(rowIndex, colIndex)}
                  style={{ cursor: 'pointer' }}
                >
                  <Piece
                    type={piece.type}
                    side={piece.side}
                    x={pos.x}
                    y={pos.y}
                    isSelected={isSelected}
                  />
                </g>
              );
            })
          )}
        </svg>

        {/* Game info */}
        <div className="game-info">
          <div className="player-info">
            <span className={`player ${currentPlayer}`}>
              {currentPlayer === 'red' ? '🔴 Red' : '⚫ Black'} Player
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