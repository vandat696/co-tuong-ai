import React from 'react';

const Piece = ({ type, side, x, y, isSelected }) => {
  // Piece types: advisor, elephant, horse, chariot, cannon, pawn
  // side: 'red' or 'black'

  const pieceSymbols = {
    advisor: { black: '士', red: '仕' },
    elephant: { black: '象', red: '相' },
    horse: { black: '馬', red: '傌' },
    chariot: { black: '車', red: '俥' },
    cannon: { black: '砲', red: '炮' },
    pawn: { black: '卒', red: '兵' },
    king: { black: '將', red: '帥' },
  };

  const symbol = pieceSymbols[type]?.[side] || '?';

  return (
    <g
      className={`piece ${side} ${type} ${isSelected ? 'selected' : ''}`}
    >
      {/* 背景圆圈 */}
      <circle
        cx={x}
        cy={y}
        r="24"
        fill={side === 'red' ? '#ff6b6b' : '#333'}
        stroke={isSelected ? '#FFD700' : '#000'}
        strokeWidth={isSelected ? '3' : '2'}
      />

      {/* 棋子内部圆圈（凹陷效果） */}
      <circle
        cx={x}
        cy={y}
        r="20"
        fill={side === 'red' ? '#ff9999' : '#666'}
        opacity="0.6"
      />

      {/* 文字 */}
      <text
        x={x}
        y={y}
        textAnchor="middle"
        dominantBaseline="middle"
        fontSize="20"
        fontWeight="bold"
        fill={side === 'red' ? '#8b0000' : '#fff'}
        fontFamily="SimSun, serif"
      >
        {symbol}
      </text>

      {/* 选中时的光晕效果 */}
      {isSelected && (
        <circle
          cx={x}
          cy={y}
          r="28"
          fill="none"
          stroke="#FFD700"
          strokeWidth="1"
          opacity="0.7"
          strokeDasharray="5,5"
        />
      )}
    </g>
  );
};

export default Piece;
