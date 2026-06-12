import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { fetchAIMove, fetchAIVersions } from "../api";
import { XiangqiRules } from "../game/XiangqiRules";

const HUMAN = "human";

const FALLBACK_AI_VERSIONS = [
  {
    id: "v1_initial",
    order: 1,
    name: "V1 - AI ban dau",
    description: "Mo phong moc khoi dau bang engine Python voi gioi han tim kiem nho.",
    engine: "python",
    max_depth: 2,
    time_limit: 0.15,
  },
  {
    id: "v2_current",
    order: 2,
    name: "V2 - AI Python hien tai",
    description: "Alpha-Beta, Iterative Deepening, TT va Quiescence Search.",
    engine: "python",
    max_depth: 5,
    time_limit: 0.5,
  },
  {
    id: "v3_wukong",
    order: 3,
    name: "V3 - WukongJS tham khao",
    description: "WukongJS 1.0 dung de doi chieu voi AI Python.",
    engine: "wukong",
    max_depth: 3,
    time_limit: 0,
  },
];

const emptyStats = () => ({
  red: { moves: 0, totalMs: 0, lastMs: 0 },
  black: { moves: 0, totalMs: 0, lastMs: 0 },
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
  const [controllers, setControllers] = useState({ red: HUMAN, black: "v2_current" });
  const [isRunning, setIsRunning] = useState(true);
  const [isThinking, setIsThinking] = useState(false);
  const [playbackDelay, setPlaybackDelay] = useState(450);
  const [halfMoveClock, setHalfMoveClock] = useState(0);
  const [history, setHistory] = useState([]);
  const [moveLog, setMoveLog] = useState([]);
  const [stats, setStats] = useState(emptyStats);
  const [arenaError, setArenaError] = useState("");
  const thinkingRef = useRef(false);

  useEffect(() => {
    fetchAIVersions()
      .then(({ versions }) => setAIVersions(versions))
      .catch(() => setArenaError("Khong tai duoc danh sach AI; dang dung cau hinh mac dinh."));
  }, []);

  const gameStatus = useMemo(
    () => XiangqiRules.getGameStatus(board, currentPlayer),
    [board, currentPlayer],
  );

  const currentController = controllers[currentPlayer];

  const handlePieceClick = useCallback(
    (row, col) => {
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
          setBoard(XiangqiRules.applyMove(board, fromRow, fromCol, row, col));
          setCurrentPlayer(XiangqiRules.getOpponent(currentPlayer));
          setLastAIMove(null);
          setSelectedPos(null);
          setValidMoves([]);
          setHalfMoveClock(0);
          setHistory([]);
          setMoveLog((items) => [
            ...items.slice(-39),
            { side: currentPlayer, controller: HUMAN, from: [fromRow, fromCol], to: [row, col] },
          ]);
          return;
        }
      }

      if (piece?.side === currentPlayer) {
        setSelectedPos([row, col]);
        setValidMoves(XiangqiRules.getLegalMoves(board, row, col));
      } else {
        setSelectedPos(null);
        setValidMoves([]);
      }
    },
    [board, currentController, currentPlayer, gameStatus.isCheckmate, isThinking, selectedPos, validMoves],
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

        const isLegal = XiangqiRules.isLegalMove(
          board,
          aiMove.from_row,
          aiMove.from_col,
          aiMove.to_row,
          aiMove.to_col,
          currentPlayer,
        );
        if (!isLegal) throw new Error(`${aiMove.ai_name} tra ve nuoc di khong hop le.`);

        await new Promise((resolve) => setTimeout(resolve, playbackDelay));
        if (cancelled) return;

        setBoard(
          XiangqiRules.applyMove(
            board,
            aiMove.from_row,
            aiMove.from_col,
            aiMove.to_row,
            aiMove.to_col,
          ),
        );
        setHalfMoveClock(aiMove.half_move_clock);
        setHistory(aiMove.history);
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
        setCurrentPlayer(XiangqiRules.getOpponent(currentPlayer));
      } catch (error) {
        if (!cancelled) {
          setArenaError(error.response?.data?.detail || error.message || "AI move failed.");
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
