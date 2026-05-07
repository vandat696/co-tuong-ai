import React from 'react';

const Piece = ({
  type,
  side,
  x,
  y,
  isSelected,
  isAiLastMoveTarget,
  onClick
}) => {
  const pieceSymbols = {
    advisor: { red: '士', black: '将' },
    elephant: { red: '象', black: '相' },
    horse: { red: '馬', black: '马' },
    chariot: { red: '車', black: '车' },
    cannon: { red: '砲', black: '炮' },
    pawn: { red: '兵', black: '卒' },
    king: { red: '帥', black: '帅' },
  };

  const symbol = pieceSymbols[type]?.[side] || '?';

  return (
    <g
      className={`piece ${side} ${type} ${isSelected ? 'selected' : ''}`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* 背景圆圈 */}
      <circle
        cx={x}
        cy={y}
        r="24"
        fill={side === 'red' ? '#ff6b6b' : '#333'}
        stroke={isSelected ? '#FFD700' : isAiLastMoveTarget ? '#007bff' : '#000'}
        strokeWidth={isSelected || isAiLastMoveTarget ? '3' : '2'}
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

      {/* Marker vàng của người chơi */}
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

      {/* Marker xanh của AI - nằm trên quân cờ */}
      {!isSelected && isAiLastMoveTarget && (
        <circle
          cx={x}
          cy={y}
          r="28"
          fill="none"
          stroke="#00bfff"
          strokeWidth="1.2"
          opacity="0.9"
          strokeDasharray="5,5"
          className="ai-target-ring"
        />
      )}
    </g>
  );
};

export default Piece;