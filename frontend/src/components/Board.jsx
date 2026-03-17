import React, { useState } from 'react';
import './Board.css';

const Board = () => {
  // Trạng thái bàn cờ (10 hàng x 9 cột)
  const [board, setBoard] = useState(
    Array(10).fill(null).map(() => Array(9).fill(0))
  );

  // Kích thước ô (pixels giữa các giao điểm)
  const CELL_SIZE = 60;
  const PADDING = 20; // Lề ngoài của bàn
  const BOARD_WIDTH = 9 * CELL_SIZE + PADDING * 2;  // 9 cột
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

          
        </svg>

        {/* Lớp overlay để xử lý click - ẩn nhưng có thể tương tác */}
        <div className="piece-overlay">
          {board.map((row, rowIndex) => (
            row.map((cell, colIndex) => {
              const pos = getPositionByGrid(rowIndex, colIndex);
              return (
                <div
                  key={`${rowIndex}-${colIndex}`}
                  className="piece-slot"
                  style={{
                    left: `${pos.x}px`,
                    top: `${pos.y}px`
                  }}
                  onClick={() => console.log(`Click giao điểm: [${rowIndex}, ${colIndex}]`)}
                  title={`[${rowIndex}, ${colIndex}]`}
                >
                  {/* Quân cờ sẽ được thêm ở đây */}
                </div>
              );
            })
          ))}
        </div>
      </div>
    </div>
  );
};

export default Board;