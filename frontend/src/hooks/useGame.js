import { useCallback, useEffect, useRef, useState } from "react";
import { applyPlayerMove, fetchAIMove, fetchAIVersions, fetchLegalMoves } from "../api";
import { BoardUtils } from "../game/BoardUtils";

const HUMAN = "human";

const FALLBACK_AI_VERSIONS = [
  {
    id: "python_current",
    order: 1,
    name: "V1 - Minimax Alpha-Beta",
    description: "Phiên bản chính đang được phát triển trong dự án.",
    engine: "Python",
    runner: "python",
    search: "Minimax, Alpha-Beta, đào sâu lặp, bảng chuyển vị và tìm kiếm tĩnh.",
    evaluation: "Tapered Evaluation kết hợp giá trị quân và bảng điểm vị trí.",
    max_depth: 5,
    time_limit: 0.5,
  },
  {
    id: "wukong_reference",
    order: 2,
    name: "V2 - WukongJS Negamax",
    description: "WukongJS 1.0 dùng làm đối thủ tham chiếu.",
    engine: "JavaScript / Node.js",
    runner: "wukong",
    search: "Negamax, Alpha-Beta, TT, Null Move, Futility, LMR và PVS.",
    evaluation: "Giá trị quân cờ kết hợp bảng điểm vị trí.",
    max_depth: 3,
    time_limit: 0,
  },
  {
    id: "python_v3",
    order: 3,
    name: "V3 - Mate-Aware Negamax",
    description: "Engine xử lý chiếu hết",
    engine: "Python",
    runner: "python_v3",
    search: "Negamax, Alpha-Beta, Zobrist TT, PVS, LMR, Null Move, Futility, Razoring và quiescence có xử lý chiếu.",
    evaluation: "Tapered Evaluation kết hợp mate-distance score.",
    max_depth: 5,
    time_limit: 0.5,
  },
];

const emptyStats = () => ({
  red: { moves: 0, totalMs: 0, lastMs: 0 },
  black: { moves: 0, totalMs: 0, lastMs: 0 },
});

const emptyGameStatus = {
  checkedSide: null,
  isCheckmate: false,
  winner: null,
  checkedKingPos: null,
};

const normalizeStatus = (status) => ({
  checkedSide: status?.checked_side ?? null,
  isCheckmate: status?.is_checkmate ?? false,
  winner: status?.winner ?? null,
  checkedKingPos: status?.checked_king_pos ?? null,
});

const createInitialBoard = () => {
  const board = Array(10)
    .fill(null)
    .map(() => Array(9).fill(null));

  const backRank = ["chariot", "horse", "elephant", "advisor", "king", "advisor", "elephant", "horse", "chariot"];
  backRank.forEach((type, col) => {
    board[0][col] = { type, side: "black" };
    board[9][col] = { type, side: "red" };
  });

  [1, 7].forEach((col) => {
    board[2][col] = { type: "cannon", side: "black" };
    board[7][col] = { type: "cannon", side: "red" };
  });

  [0, 2, 4, 6, 8].forEach((col) => {
    board[3][col] = { type: "pawn", side: "black" };
    board[6][col] = { type: "pawn", side: "red" };
  });

  let id = 0;
  board.forEach((row) => {
    row.forEach((piece) => {
      if (piece) piece.id = `piece-${id++}`;
    });
  });

  return board;
};

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
      return piece.side === "red" ? typeMap[piece.type] : -typeMap[piece.type];
    }),
  );
};

export const useGame = () => {
  const [board, setBoard] = useState(createInitialBoard);
  const [selectedPos, setSelectedPos] = useState(null);
  const [validMoves, setValidMoves] = useState([]);
  const [currentPlayer, setCurrentPlayer] = useState("red");
  const [lastAIMove, setLastAIMove] = useState(null);
  const [aiVersions, setAIVersions] = useState(FALLBACK_AI_VERSIONS);
  const [controllers, setControllers] = useState({ red: HUMAN, black: "python_current" });
  const [isRunning, setIsRunning] = useState(true);
  const [isThinking, setIsThinking] = useState(false);
  const [playbackDelay, setPlaybackDelay] = useState(450);
  const [halfMoveClock, setHalfMoveClock] = useState(0);
  const [history, setHistory] = useState([]);
  const [moveLog, setMoveLog] = useState([]);
  const [stats, setStats] = useState(emptyStats);
  const [arenaError, setArenaError] = useState("");
  const [gameStatus, setGameStatus] = useState(emptyGameStatus);
  const thinkingRef = useRef(false);

  useEffect(() => {
    fetchAIVersions()
      .then(({ versions }) => setAIVersions(versions))
      .catch(() => setArenaError("Không tải được danh sách AI; đang dùng cấu hình mặc định."));
  }, []);

  const currentController = controllers[currentPlayer];

  const handlePieceClick = useCallback(
    async (row, col) => {
      if (gameStatus.isCheckmate || isThinking || currentController !== HUMAN) return;

      const piece = board[row][col];
      if (selectedPos?.[0] === row && selectedPos?.[1] === col) {
        setSelectedPos(null);
        setValidMoves([]);
        return;
      }

      if (selectedPos) {
        const [fromRow, fromCol] = selectedPos;
        const canMove = validMoves.some(([r, c]) => r === row && c === col);

        if (canMove) {
          try {
            const result = await applyPlayerMove({
              boardState: boardToIntArray(board),
              isRedTurn: currentPlayer === "red",
              fromRow,
              fromCol,
              toRow: row,
              toCol: col,
              halfMoveClock,
              history,
            });
            const nextBoard = BoardUtils.applyMove(board, fromRow, fromCol, row, col);
            setBoard(nextBoard);
            setCurrentPlayer(BoardUtils.getOpponent(currentPlayer));
            setLastAIMove(null);
            setSelectedPos(null);
            setValidMoves([]);
            setHalfMoveClock(result.half_move_clock);
            setHistory(result.history);
            setGameStatus(normalizeStatus(result.status));
            setMoveLog((items) => [
              ...items.slice(-39),
              { side: currentPlayer, controller: HUMAN, from: [fromRow, fromCol], to: [row, col] },
            ]);
          } catch (error) {
            setArenaError(error.response?.data?.detail || "Backend từ chối nước đi.");
          }
          return;
        }
      }

      if (piece?.side === currentPlayer) {
        try {
          const result = await fetchLegalMoves({
            boardState: boardToIntArray(board),
            isRedTurn: currentPlayer === "red",
            row,
            col,
            halfMoveClock,
            history,
          });
          setSelectedPos([row, col]);
          setValidMoves(result.moves);
          setGameStatus(normalizeStatus(result.status));
          setArenaError("");
        } catch (error) {
          setArenaError(error.response?.data?.detail || "Không lấy được nước đi hợp lệ.");
        }
      } else {
        setSelectedPos(null);
        setValidMoves([]);
      }
    },
    [board, currentController, currentPlayer, gameStatus.isCheckmate, halfMoveClock, history, isThinking, selectedPos, validMoves],
  );

  useEffect(() => {
    if (
      currentController === HUMAN ||
      !isRunning ||
      thinkingRef.current ||
      gameStatus.isCheckmate
    ) {
      return undefined;
    }

    let cancelled = false;

    const playAIMove = async () => {
      thinkingRef.current = true;
      setIsThinking(true);
      setArenaError("");

      try {
        const aiMove = await fetchAIMove({
          boardState: boardToIntArray(board),
          isRedTurn: currentPlayer === "red",
          aiVersion: currentController,
          halfMoveClock,
          history,
        });

        if (cancelled) return;

        await new Promise((resolve) => setTimeout(resolve, playbackDelay));
        if (cancelled) return;

        setBoard(
          BoardUtils.applyMove(board, aiMove.from_row, aiMove.from_col, aiMove.to_row, aiMove.to_col),
        );
        setHalfMoveClock(aiMove.half_move_clock);
        setHistory(aiMove.history);
        setGameStatus(normalizeStatus(aiMove.status));
        setLastAIMove({
          from: [aiMove.from_row, aiMove.from_col],
          to: [aiMove.to_row, aiMove.to_col],
          side: currentPlayer,
        });
        setMoveLog((items) => [
          ...items.slice(-39),
          {
            side: currentPlayer,
            controller: aiMove.ai_name,
            from: [aiMove.from_row, aiMove.from_col],
            to: [aiMove.to_row, aiMove.to_col],
            elapsedMs: aiMove.elapsed_ms,
            score: aiMove.score,
          },
        ]);
        setStats((current) => ({
          ...current,
          [currentPlayer]: {
            moves: current[currentPlayer].moves + 1,
            totalMs: current[currentPlayer].totalMs + aiMove.elapsed_ms,
            lastMs: aiMove.elapsed_ms,
          },
        }));
        setCurrentPlayer(BoardUtils.getOpponent(currentPlayer));
      } catch (error) {
        if (!cancelled) {
          setArenaError(error.response?.data?.detail || error.message || "AI không thể thực hiện nước đi.");
          setIsRunning(false);
        }
      } finally {
        if (!cancelled) {
          thinkingRef.current = false;
          setIsThinking(false);
        }
      }
    };

    playAIMove();
    return () => {
      cancelled = true;
      thinkingRef.current = false;
      setIsThinking(false);
    };
  }, [
    board,
    currentController,
    currentPlayer,
    gameStatus.isCheckmate,
    halfMoveClock,
    history,
    isRunning,
    playbackDelay,
  ]);

  const resetGame = useCallback(() => {
    setBoard(createInitialBoard());
    setSelectedPos(null);
    setValidMoves([]);
    setCurrentPlayer("red");
    setLastAIMove(null);
    setHalfMoveClock(0);
    setHistory([]);
    setMoveLog([]);
    setStats(emptyStats());
    setArenaError("");
    setGameStatus(emptyGameStatus);
  }, []);

  const setController = useCallback((side, controller) => {
    setControllers((current) => ({ ...current, [side]: controller }));
    setSelectedPos(null);
    setValidMoves([]);
    setArenaError("");
  }, []);

  return {
    board,
    selectedPos,
    validMoves,
    currentPlayer,
    lastAIMove,
    gameStatus,
    handlePieceClick,
    resetGame,
    aiVersions,
    controllers,
    setController,
    isRunning,
    setIsRunning,
    isThinking,
    playbackDelay,
    setPlaybackDelay,
    moveLog,
    stats,
    arenaError,
  };
};
