"""Fixed-size transposition table with mate-score normalization."""

from dataclasses import dataclass


EXACT = "EXACT"
LOWER = "LOWER"
UPPER = "UPPER"


@dataclass
class TTEntry:
    key: int
    depth: int
    score: int
    flag: str
    best_move: int | None


class TranspositionTable:
    def __init__(self, capacity, mate_threshold):
        self.entries = [None] * capacity
        self.mate_threshold = mate_threshold

    def clear(self):
        self.entries = [None] * len(self.entries)

    def probe(self, key):
        entry = self.entries[key % len(self.entries)]
        return entry if entry is not None and entry.key == key else None

    def read_score(self, entry, ply):
        score = entry.score
        if score > self.mate_threshold:
            return score - ply
        if score < -self.mate_threshold:
            return score + ply
        return score

    def store(self, key, depth, score, flag, best_move, ply):
        current = self.entries[key % len(self.entries)]
        if current is not None and current.key == key and current.depth > depth:
            return

        stored_score = score
        if score > self.mate_threshold:
            stored_score += ply
        elif score < -self.mate_threshold:
            stored_score -= ply

        self.entries[key % len(self.entries)] = TTEntry(
            key,
            depth,
            stored_score,
            flag,
            best_move,
        )
