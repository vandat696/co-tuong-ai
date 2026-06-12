import { BoardUtils } from "./BoardUtils";
import { PieceMoveGenerator } from "./PieceMoveGenerator";

export class XiangqiRules {
  static getLegalMoves(board, row, col, history = []) {
    const piece = BoardUtils.getPiece(board, row, col);
    if (!piece) return [];

    return PieceMoveGenerator.getPseudoMoves(board, row, col, piece).filter(([toRow, toCol]) => {
      const nextBoard = BoardUtils.applyMove(board, row, col, toRow, toCol);
      const repeatsForThirdTime = history.filter(
        (state) => state === BoardUtils.stateHash(nextBoard),
      ).length >= 2;
      return !this.isKingInCheck(nextBoard, piece.side) && !repeatsForThirdTime;
    });
  }

  static isLegalMove(board, fromRow, fromCol, toRow, toCol, side, history = []) {
    const piece = BoardUtils.getPiece(board, fromRow, fromCol);
    if (!piece || piece.side !== side) return false;

    return this.getLegalMoves(board, fromRow, fromCol, history).some(
      ([row, col]) => row === toRow && col === toCol,
    );
  }

  static getGameStatus(board, currentPlayer, history = []) {
    const checkedSide = this.isKingInCheck(board, currentPlayer) ? currentPlayer : null;
    const isCheckmate = Boolean(checkedSide) && !this.hasLegalMove(board, currentPlayer, history);

    return {
      checkedSide,
      isCheckmate,
      winner: isCheckmate ? BoardUtils.getOpponent(currentPlayer) : null,
      checkedKingPos: checkedSide ? BoardUtils.findKing(board, checkedSide) : null,
    };
  }

  static getFallbackMove(board, side, history = []) {
    for (let row = 0; row < BoardUtils.ROWS; row++) {
      for (let col = 0; col < BoardUtils.COLS; col++) {
        const piece = BoardUtils.getPiece(board, row, col);
        if (!piece || piece.side !== side) continue;

        const legalMoves = this.getLegalMoves(board, row, col, history);
        if (legalMoves.length === 0) continue;

        const [toRow, toCol] = legalMoves[0];
        return {
          from_row: row,
          from_col: col,
          to_row: toRow,
          to_col: toCol,
          score: 0,
        };
      }
    }

    return null;
  }

  static hasLegalMove(board, side, history = []) {
    for (let row = 0; row < BoardUtils.ROWS; row++) {
      for (let col = 0; col < BoardUtils.COLS; col++) {
        const piece = BoardUtils.getPiece(board, row, col);

        if (piece?.side === side && this.getLegalMoves(board, row, col, history).length > 0) {
          return true;
        }
      }
    }

    return false;
  }

  static isKingInCheck(board, side) {
    const kingPos = BoardUtils.findKing(board, side);
    if (!kingPos) return true;

    const [kingRow, kingCol] = kingPos;
    if (this.isKingsFacing(board)) return true;

    for (let row = 0; row < BoardUtils.ROWS; row++) {
      for (let col = 0; col < BoardUtils.COLS; col++) {
        const piece = BoardUtils.getPiece(board, row, col);
        if (!piece || piece.side === side) continue;

        const attacksKing = PieceMoveGenerator.getPseudoMoves(board, row, col, piece).some(
          ([r, c]) => r === kingRow && c === kingCol,
        );

        if (attacksKing) return true;
      }
    }

    return false;
  }

  static isKingsFacing(board) {
    const redKing = BoardUtils.findKing(board, "red");
    const blackKing = BoardUtils.findKing(board, "black");

    if (!redKing || !blackKing || redKing[1] !== blackKing[1]) return false;

    const col = redKing[1];
    const startRow = Math.min(redKing[0], blackKing[0]);
    const endRow = Math.max(redKing[0], blackKing[0]);

    for (let row = startRow + 1; row < endRow; row++) {
      if (!BoardUtils.isEmpty(board, row, col)) return false;
    }

    return true;
  }

  static applyMove(board, fromRow, fromCol, toRow, toCol) {
    return BoardUtils.applyMove(board, fromRow, fromCol, toRow, toCol);
  }

  static getOpponent(side) {
    return BoardUtils.getOpponent(side);
  }
}
