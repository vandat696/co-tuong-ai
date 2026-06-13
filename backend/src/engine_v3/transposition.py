"""Fixed-size allocation-free transposition table."""

EXACT = 0
LOWER = 1
UPPER = 2


class TranspositionTable:
    def __init__(self, capacity, mate_threshold):
        self.capacity = capacity
        self.mate_threshold = mate_threshold
        self.keys = [0] * capacity
        self.depths = [-1] * capacity
        self.scores = [0] * capacity
        self.flags = [EXACT] * capacity
        self.moves = [0] * capacity

    def clear(self):
        self.depths = [-1] * self.capacity

    def probe(self, key):
        index = key % self.capacity
        return index if self.depths[index] >= 0 and self.keys[index] == key else -1

    def read_score(self, index, ply):
        score = self.scores[index]
        if score > self.mate_threshold:
            return score - ply
        if score < -self.mate_threshold:
            return score + ply
        return score

    def store(self, key, depth, score, flag, best_move, ply):
        index = key % self.capacity
        if self.keys[index] == key and self.depths[index] > depth:
            return

        if score > self.mate_threshold:
            score += ply
        elif score < -self.mate_threshold:
            score -= ply

        self.keys[index] = key
        self.depths[index] = depth
        self.scores[index] = score
        self.flags[index] = flag
        self.moves[index] = best_move or 0
