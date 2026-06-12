export class BoardUtils {
  static ROWS = 10;
  static COLS = 9;

  static isInBounds(row, col) {
    return row >= 0 && row < this.ROWS && col >= 0 && col < this.COLS;
  }

  static isInPalace(row, col, side) {
    if (side === "red") return row >= 7 && row <= 9 && col >= 3 && col <= 5;
    return row >= 0 && row <= 2 && col >= 3 && col <= 5;
  }

  static getPiece(board, row, col) {
    return this.isInBounds(row, col) ? board[row][col] : null;
  }

  static isEmpty(board, row, col) {
    return this.getPiece(board, row, col) === null;
  }

  static isEnemy(board, row, col, side) {
    const piece = this.getPiece(board, row, col);
    return Boolean(piece && piece.side !== side);
  }

  static canLand(board, row, col, side) {
    return (
      this.isInBounds(row, col) &&
      (this.isEmpty(board, row, col) || this.isEnemy(board, row, col, side))
    );
  }

  static applyMove(board, fromRow, fromCol, toRow, toCol) {
    const nextBoard = board.map((row) => [...row]);
    nextBoard[toRow][toCol] = nextBoard[fromRow][fromCol];
    nextBoard[fromRow][fromCol] = null;
    return nextBoard;
  }

  static findKing(board, side) {
    for (let row = 0; row < this.ROWS; row++) {
      for (let col = 0; col < this.COLS; col++) {
        const piece = board[row][col];

        if (piece?.type === "king" && piece.side === side) {
          return [row, col];
        }
      }
    }

    return null;
  }

  static getOpponent(side) {
    return side === "red" ? "black" : "red";
  }
}
