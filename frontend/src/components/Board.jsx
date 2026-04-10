import React from 'react';
import { useGame } from '../hooks/useGame';
import Piece from './Piece';
import './Board.css';

const Board = () => {
  // Game state management
  const { board, selectedPos, validMoves, currentPlayer, isAIThinking, gameMode, handlePieceClick, setGameMode, resetGame } = useGame();

  console.log('Board rendered - Game is ready to play');
  console.log('Current player:', currentPlayer);
  console.log('Selected pos:', selectedPos);
  console.log('Valid moves:', validMoves);

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
          style={{ border: '2px solid #8b4513', pointerEvents: 'auto' }}
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

          {/* Hiển thị các quân cờ và hợp lệ moves */}
          {board.map((row, rowIndex) =>
            row.map((piece, colIndex) => {
              const pos = getPositionByGrid(rowIndex, colIndex);
              const isSelected = selectedPos && selectedPos[0] === rowIndex && selectedPos[1] === colIndex;
              
              if (piece) {
                // Render piece
                return (
                  <g
                    key={`piece-${rowIndex}-${colIndex}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (!isAIThinking) {
                        console.log('Click on piece at', rowIndex, colIndex);
                        handlePieceClick(rowIndex, colIndex);
                      }
                    }}
                    style={{
                      cursor: isAIThinking ? 'not-allowed' : 'pointer',
                      pointerEvents: 'auto',
                      opacity: isAIThinking ? 0.6 : 1,
                      transition: 'opacity 0.2s ease'
                    }}
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
              }
              
              // Render empty square clickable if it's a valid move destination
              const isValidDest = validMoves.some(([r, c]) => r === rowIndex && c === colIndex);
              if (isValidDest) {
                return (
                  <circle
                    key={`empty-${rowIndex}-${colIndex}`}
                    cx={pos.x}
                    cy={pos.y}
                    r="12"
                    fill="#00ff00"
                    opacity="0.6"
                    style={{
                      cursor: 'pointer',
                      pointerEvents: 'auto'
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      if (!isAIThinking) {
                        console.log('Click on empty square at', rowIndex, colIndex);
                        handlePieceClick(rowIndex, colIndex);
                      }
                    }}
                  />
                );
              }
              
              return null;
            })
          )}
        </svg>

        {/* Game info */}
        <div className="game-info">
          <div className="player-info">
            <span className={`player ${currentPlayer}`}>
              {isAIThinking ? '🤔 AI thinking...' : `${currentPlayer === 'red' ? '🔴 Red' : '⚫ Black'} Player`}
            </span>
          </div>
          
          <div className="game-controls">
            <div className="mode-toggle">
              <button 
                className={`mode-btn ${gameMode === 'ai' ? 'active' : ''}`}
                onClick={() => setGameMode('ai')}
                disabled={isAIThinking}
              >
                🤖 vs AI
              </button>
              <button 
                className={`mode-btn ${gameMode === 'pvp' ? 'active' : ''}`}
                onClick={() => setGameMode('pvp')}
                disabled={isAIThinking}
              >
                👥 PvP
              </button>
            </div>
            <button className="reset-btn" onClick={resetGame} disabled={isAIThinking}>
              ↻ Reset
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Board;