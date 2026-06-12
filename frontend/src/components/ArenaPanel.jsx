const SIDE_ORDER = ["black", "red"];

const ArenaPanel = ({ game }) => {
  const {
    aiVersions,
    arenaError,
    controllers,
    currentPlayer,
    gameStatus,
    isRunning,
    isThinking,
    moveLog,
    playbackDelay,
    resetGame,
    setController,
    setIsRunning,
    setPlaybackDelay,
    stats,
  } = game;

  const controllerName = (controller) => {
    if (controller === "human") return "Người chơi";
    return aiVersions.find((version) => version.id === controller)?.name || controller;
  };

  const averageTime = (side) => {
    const sideStats = stats[side];
    return sideStats.moves ? Math.round(sideStats.totalMs / sideStats.moves) : 0;
  };

  const selectedVersion = (side) =>
    aiVersions.find((version) => version.id === controllers[side]);

  const coordinate = ([row, col]) =>
    `${String.fromCharCode("a".charCodeAt(0) + col)}${9 - row}`;

  return (
    <aside className="arena-panel">

      {SIDE_ORDER.map((side) => {
        const version = selectedVersion(side);

        return (
          <section className={`controller-card ${side}`} key={side}>
            <label htmlFor={`${side}-controller`}>
              Bên {side === "red" ? "Đỏ" : "Đen"}
            </label>
            <select
              id={`${side}-controller`}
              value={controllers[side]}
              onChange={(event) => setController(side, event.target.value)}
              disabled={isThinking}
            >
              <option value="human">Người chơi</option>
              {aiVersions.map((item) => (
                <option value={item.id} key={item.id}>
                  {item.name}
                </option>
              ))}
            </select>

            {version && (
              <div className="version-details">
                <p>{version.description}</p>
                <dl>
                  <div>
                    <dt>Thuật toán</dt>
                    <dd>{version.search}</dd>
                  </div>
                  <div>
                    <dt>Hàm đánh giá</dt>
                    <dd>{version.evaluation}</dd>
                  </div>
                  <div>
                    <dt>Thiết lập</dt>
                    <dd>
                      {version.engine}, sâu tối đa {version.max_depth}
                      {version.time_limit ? `, ${version.time_limit} giây/nước` : ""}
                    </dd>
                  </div>
                </dl>
              </div>
            )}

            <small>
              {stats[side].moves} nước AI · Trung bình {averageTime(side)} ms · Gần nhất{" "}
              {Math.round(stats[side].lastMs)} ms
            </small>
          </section>
        );
      })}

      <div className="arena-actions">
        <button
          className="arena-primary"
          onClick={() => setIsRunning((running) => !running)}
          disabled={gameStatus.isCheckmate}
        >
          {isRunning ? "Tạm dừng AI" : "Chạy AI"}
        </button>
        <button onClick={resetGame}>Ván mới</button>
      </div>

      <label className="speed-control">
        <span>Độ trễ quan sát: {playbackDelay} ms</span>
        <input
          type="range"
          min="0"
          max="1500"
          step="100"
          value={playbackDelay}
          onChange={(event) => setPlaybackDelay(Number(event.target.value))}
        />
      </label>

      <div className="arena-status">
        <strong>
          {gameStatus.isCheckmate
            ? `Chiếu hết · Bên ${gameStatus.winner === "red" ? "Đỏ" : "Đen"} thắng`
            : gameStatus.checkedSide
              ? `Bên ${gameStatus.checkedSide === "red" ? "Đỏ" : "Đen"} đang bị chiếu`
              : isThinking
            ? `${controllerName(controllers[currentPlayer])} đang suy nghĩ...`
            : isRunning
              ? `Lượt bên ${currentPlayer === "red" ? "Đỏ" : "Đen"}`
              : "Đấu trường đang tạm dừng"}
        </strong>
        {arenaError && <span className="arena-error">{arenaError}</span>}
      </div>

      <div className="move-log">
        <h2>Lịch sử nước đi</h2>
        {moveLog.length === 0 ? (
          <p>Chưa có nước đi.</p>
        ) : (
          [...moveLog].reverse().map((move, index) => (
            <div className={`move-row ${move.side}`} key={`${moveLog.length}-${index}`}>
              <span className="move-side">{move.side === "red" ? "Đỏ" : "Đen"}</span>
              <span className="move-controller">{move.controller}</span>
              <code className="move-from">{coordinate(move.from)}</code>
              <span className="move-arrow">→</span>
              <code className="move-to">{coordinate(move.to)}</code>
              <span className="move-meta">
                {move.elapsedMs ? `${Math.round(move.elapsedMs)} ms · điểm ${move.score}` : "người chơi"}
              </span>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};

export default ArenaPanel;
