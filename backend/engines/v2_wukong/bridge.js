const { Engine } = require("./wukong.js");

const fen = process.argv[2];
const depth = Number(process.argv[3] || 64);
const timeLimitMs = Number(process.argv[4] || 500);

if (!fen) {
  throw new Error("Missing FEN");
}

const engine = new Engine();
engine.setBoard(fen);
engine.setTimeControl({
  timeSet: 1,
  stopTime: Date.now() + timeLimitMs,
  stopped: 0,
  time: timeLimitMs,
});

const originalLog = console.log;
console.log = () => {};
const move = engine.search(depth);
console.log = originalLog;
const searchInfo = engine.getSearchInfo();

const moveText = engine.moveToString(move);
const fileToCol = (file) => file.charCodeAt(0) - "a".charCodeAt(0);
const rankToRow = (rank) => 9 - Number(rank);

process.stdout.write(
  JSON.stringify({
    from_row: rankToRow(moveText[1]),
    from_col: fileToCol(moveText[0]),
    to_row: rankToRow(moveText[3]),
    to_col: fileToCol(moveText[2]),
    completed_depth: searchInfo.completedDepth,
    nodes: searchInfo.nodes,
    stopped: Boolean(searchInfo.stopped),
    search_elapsed_ms: searchInfo.elapsedMs,
  }),
);
