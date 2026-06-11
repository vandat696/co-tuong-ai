import { BoardUtils } from "./BoardUtils";

export class PieceMoveGenerator {
  static getPseudoMoves(board, row, col, piece) {
    const moveBuilders = {
      advisor: this.getAdvisorMoves,
      cannon: this.getCannonMoves,
      chariot: this.getChariotMoves,
      elephant: this.getElephantMoves,
      horse: this.getHorseMoves,
      king: this.getKingMoves,
      pawn: this.getPawnMoves,
    };

    const buildMoves = moveBuilders[piece.type];
    return buildMoves ? buildMoves.call(this, board, row, col, piece) : [];
  }

  static getChariotMoves(board, row, col, piece) {
    return this.getLineMoves(board, row, col, piece, { cannonCapture: false });
  }

  static getCannonMoves(board, row, col, piece) {
    return this.getLineMoves(board, row, col, piece, { cannonCapture: true });
  }

  static getHorseMoves(board, row, col, piece) {
    const moves = [];
    const jumps = [
      [1, 2],
      [1, -2],
      [-1, 2],
      [-1, -2],
      [2, 1],
      [2, -1],
      [-2, 1],
      [-2, -1],
    ];

    for (const [dr, dc] of jumps) {
      const targetRow = row + dr;
      const targetCol = col + dc;
      const blockRow = Math.abs(dr) === 2 ? row + Math.sign(dr) : row;
      const blockCol = Math.abs(dr) === 2 ? col : col + Math.sign(dc);

      if (
        BoardUtils.isEmpty(board, blockRow, blockCol) &&
        BoardUtils.canLand(board, targetRow, targetCol, piece.side)
      ) {
        moves.push([targetRow, targetCol]);
      }
    }

    return moves;
  }

  static getElephantMoves(board, row, col, piece) {
    const moves = [];
    const jumps = [
      [-2, -2],
      [-2, 2],
      [2, -2],
      [2, 2],
    ];

    for (const [dr, dc] of jumps) {
      const targetRow = row + dr;
      const targetCol = col + dc;
      const blockRow = row + dr / 2;
      const blockCol = col + dc / 2;
      const staysHome = piece.side === "red" ? targetRow >= 5 : targetRow <= 4;

      if (
        staysHome &&
        BoardUtils.isEmpty(board, blockRow, blockCol) &&
        BoardUtils.canLand(board, targetRow, targetCol, piece.side)
      ) {
        moves.push([targetRow, targetCol]);
      }
    }

    return moves;
  }

  static getAdvisorMoves(board, row, col, piece) {
    const moves = [];
    const jumps = [
      [-1, -1],
      [-1, 1],
      [1, -1],
      [1, 1],
    ];

    for (const [dr, dc] of jumps) {
      const targetRow = row + dr;
      const targetCol = col + dc;

      if (
        BoardUtils.isInPalace(targetRow, targetCol, piece.side) &&
        BoardUtils.canLand(board, targetRow, targetCol, piece.side)
      ) {
        moves.push([targetRow, targetCol]);
      }
    }

    return moves;
  }

  static getKingMoves(board, row, col, piece) {
    const moves = [];
    const directions = [
      [0, 1],
      [0, -1],
      [1, 0],
      [-1, 0],
    ];

    for (const [dr, dc] of directions) {
      const targetRow = row + dr;
      const targetCol = col + dc;

      if (
        BoardUtils.isInPalace(targetRow, targetCol, piece.side) &&
        BoardUtils.canLand(board, targetRow, targetCol, piece.side)
      ) {
        moves.push([targetRow, targetCol]);
      }
    }

    return moves;
  }

  static getPawnMoves(board, row, col, piece) {
    const moves = [];
    const isCrossedRiver =
      (piece.side === "red" && row <= 4) || (piece.side === "black" && row >= 5);
    const directions = piece.side === "red" ? [[-1, 0]] : [[1, 0]];

    if (isCrossedRiver) {
      directions.push([0, -1], [0, 1]);
    }

    for (const [dr, dc] of directions) {
      const targetRow = row + dr;
      const targetCol = col + dc;

      if (BoardUtils.canLand(board, targetRow, targetCol, piece.side)) {
        moves.push([targetRow, targetCol]);
      }
    }

    return moves;
  }

  static getLineMoves(board, row, col, piece, { cannonCapture }) {
    const moves = [];
    const directions = [
      [0, 1],
      [0, -1],
      [1, 0],
      [-1, 0],
    ];

    for (const [dr, dc] of directions) {
      const lineMoves = cannonCapture
        ? this.getCannonLineMoves(board, row, col, piece, dr, dc)
        : this.getChariotLineMoves(board, row, col, piece, dr, dc);

      moves.push(...lineMoves);
    }

    return moves;
  }

  static getChariotLineMoves(board, row, col, piece, dr, dc) {
    const moves = [];
    let targetRow = row + dr;
    let targetCol = col + dc;

    while (BoardUtils.isInBounds(targetRow, targetCol)) {
      if (BoardUtils.isEmpty(board, targetRow, targetCol)) {
        moves.push([targetRow, targetCol]);
      } else {
        if (BoardUtils.isEnemy(board, targetRow, targetCol, piece.side)) {
          moves.push([targetRow, targetCol]);
        }

        break;
      }

      targetRow += dr;
      targetCol += dc;
    }

    return moves;
  }

  static getCannonLineMoves(board, row, col, piece, dr, dc) {
    const moves = [];
    let targetRow = row + dr;
    let targetCol = col + dc;

    while (
      BoardUtils.isInBounds(targetRow, targetCol) &&
      BoardUtils.isEmpty(board, targetRow, targetCol)
    ) {
      moves.push([targetRow, targetCol]);
      targetRow += dr;
      targetCol += dc;
    }

    if (
      BoardUtils.isInBounds(targetRow, targetCol) &&
      !BoardUtils.isEmpty(board, targetRow, targetCol)
    ) {
      targetRow += dr;
      targetCol += dc;

      while (BoardUtils.isInBounds(targetRow, targetCol)) {
        if (BoardUtils.isEmpty(board, targetRow, targetCol)) {
          targetRow += dr;
          targetCol += dc;
        } else {
          if (BoardUtils.isEnemy(board, targetRow, targetCol, piece.side)) {
            moves.push([targetRow, targetCol]);
          }

          break;
        }
      }
    }

    return moves;
  }
}
