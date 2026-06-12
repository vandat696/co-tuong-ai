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
    if (controller === "human") return "Human";
    return aiVersions.find((version) => version.id === controller)?.name || controller;
  };

  const averageTime = (side) => {
    const sideStats = stats[side];
    return sideStats.moves ? Math.round(sideStats.totalMs / sideStats.moves) : 0;
  };

  const selectedVersion = (side) =>
    aiVersions.find((version) => version.id === controllers[side]);

  return (
    <aside className="arena-panel">
      <div>
        <p className="eyebrow">AI Arena</p>
        <h1>Quan sat va so sanh AI</h1>
        <p className="arena-copy">
          Chon bo dieu khien cho tung ben. Dat ca hai ben thanh AI de xem chung tu dau.
        </p>
      </div>

      {["red", "black"].map((side) => (
        <label className={`controller-card ${side}`} key={side}>
          <span>{side === "red" ? "Do" : "Den"}</span>
          <select
            value={controllers[side]}
            onChange={(event) => setController(side, event.target.value)}
            disabled={isThinking}
          >
            <option value="human">Human</option>
            {aiVersions.map((version) => (
              <option value={version.id} key={version.id}>
                {version.name}
              </option>
            ))}
          </select>
          {selectedVersion(side) && (
            <p className="version-description">
              {selectedVersion(side).description}
              <br />
              Engine: {selectedVersion(side).engine} | Depth {selectedVersion(side).max_depth}
              {selectedVersion(side).time_limit
                ? ` | ${selectedVersion(side).time_limit}s/nuoc`
                : ""}
            </p>
          )}
          <small>
            {stats[side].moves} nuoc AI | TB {averageTime(side)} ms | Gan nhat{" "}
            {Math.round(stats[side].lastMs)} ms
          </small>
        </label>
      ))}

      <div className="arena-actions">
        <button
          className="arena-primary"
          onClick={() => setIsRunning((running) => !running)}
          disabled={gameStatus.isCheckmate}
        >
          {isRunning ? "Tam dung AI" : "Chay AI"}
        </button>
        <button onClick={resetGame}>Van moi</button>
      </div>

      <label className="speed-control">
        <span>Do tre quan sat: {playbackDelay} ms</span>
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
          {isThinking
            ? `${controllerName(controllers[currentPlayer])} dang suy nghi...`
            : isRunning
              ? `Luot ${currentPlayer === "red" ? "Do" : "Den"}`
              : "Arena dang tam dung"}
        </strong>
        {arenaError && <span className="arena-error">{arenaError}</span>}
      </div>

      <div className="move-log">
        <h2>Lich su nuoc di</h2>
        {moveLog.length === 0 ? (
          <p>Chua co nuoc di.</p>
        ) : (
          [...moveLog].reverse().map((move, index) => (
            <div className={`move-row ${move.side}`} key={`${moveLog.length}-${index}`}>
              <span>
                {move.side === "red" ? "Do" : "Den"} / {move.controller}
              </span>
              <code>
                {move.from.join(",")} to {move.to.join(",")}
              </code>
              <small>
                {move.elapsedMs ? `${Math.round(move.elapsedMs)} ms | score ${move.score}` : "human"}
              </small>
            </div>
          ))
        )}
      </div>
    </aside>
  );
};

export default ArenaPanel;
