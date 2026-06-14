"""V3 mate-aware Negamax search with Wukong-inspired optimizations."""

from dataclasses import dataclass

from engines.v3.context import SearchContext, SearchTimeout
from engines.v3.move import move_to_coordinates
from engines.v3.ordering import PIECE_VALUES, MoveOrdering
from engines.v3.transposition import EXACT, LOWER, UPPER, TranspositionTable


MATE_SCORE = 100_000
MATE_THRESHOLD = 99_000
INFINITY = 110_000
MAX_PLY = 80
MAX_QUIESCENCE_PLY = 12
ASPIRATION_WINDOW = 50


@dataclass
class SearchStats:
    nodes: int = 0
    qnodes: int = 0
    tt_hits: int = 0
    beta_cutoffs: int = 0
    null_cutoffs: int = 0
    futility_prunes: int = 0
    razor_prunes: int = 0
    lmr_reductions: int = 0
    pvs_researches: int = 0
    completed_depth: int = 0
    used_fallback: bool = True


class AIEngineV3:
    """Negamax engine with mate-aware search and selective pruning."""

    def __init__(self, board, max_depth=5, time_limit=1.0, tt_capacity=65_536):
        self.board = board
        self.max_depth = max_depth
        self.context = SearchContext(board, time_limit)
        self.tt = TranspositionTable(tt_capacity, MATE_THRESHOLD)
        self.ordering = MoveOrdering(self.context.evaluator, MAX_PLY)
        self.stats = SearchStats()

    def get_best_move(self, is_red_turn):
        self.context.start()
        self.tt.clear()
        self.ordering.clear()
        self.stats = SearchStats()

        fallback_moves = self.context.legal_moves(is_red_turn)
        if not fallback_moves:
            return None

        best_move = self._best_static_fallback(fallback_moves, is_red_turn)
        previous_best = None
        previous_score = 0

        for depth in range(1, self.max_depth + 1):
            try:
                score, iteration_best = self._aspiration_search(
                    depth,
                    is_red_turn,
                    previous_best,
                    previous_score,
                )
            except SearchTimeout:
                break

            if iteration_best is not None:
                best_move = iteration_best
                previous_best = iteration_best
                previous_score = score
                self.stats.completed_depth = depth
                self.stats.used_fallback = False

            if abs(previous_score) >= MATE_THRESHOLD:
                break

        return move_to_coordinates(best_move)

    def _best_static_fallback(self, moves, is_red_turn):
        best_move = moves[0]
        best_score = -INFINITY

        for move in moves:
            moved_piece = self.context.piece_at_source(move)
            undo = self.context.push(move)
            try:
                score = -self.context.evaluate_for_side(not is_red_turn, dynamic=True)
                to_row, to_col = self.context.move_target(move)
                if self._is_square_attacked(to_row, to_col, not is_red_turn):
                    score -= self.context.evaluator.get_piece_value(moved_piece)
            finally:
                self.context.pop(undo)

            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def _is_square_attacked(self, target_row, target_col, by_red):
        return self.context.is_square_attacked(target_row, target_col, by_red)

    def _checking_moves(self, moves, is_red_turn):
        checking = set()
        for move in moves:
            if not self.context.position.make_move(move, is_red_turn):
                continue
            if self.context.position.is_in_check(not is_red_turn):
                checking.add(move)
            self.context.position.unmake_move()
        return checking

    def _aspiration_search(self, depth, is_red_turn, previous_best, previous_score):
        if depth <= 1:
            return self._search_root(
                depth,
                is_red_turn,
                previous_best,
                -INFINITY,
                INFINITY,
            )

        window = ASPIRATION_WINDOW
        alpha = previous_score - window
        beta = previous_score + window

        while True:
            score, best_move = self._search_root(
                depth,
                is_red_turn,
                previous_best,
                alpha,
                beta,
            )
            if score <= alpha:
                alpha = max(-INFINITY, alpha - window)
            elif score >= beta:
                beta = min(INFINITY, beta + window)
            else:
                return score, best_move
            window *= 2

    def _search_root(self, depth, is_red_turn, previous_best, alpha, beta):
        best_score = -INFINITY
        best_move = None
        pseudo_moves = self.context.pseudo_moves(is_red_turn)
        moves = self.ordering.ordered(
            self.context.position,
            pseudo_moves,
            0,
            previous_best,
            self._checking_moves(pseudo_moves, is_red_turn),
        )

        legal_count = 0
        for move in moves:
            self.context.check_time(force=True)
            undo = self.context.push(move)
            if undo is None:
                continue
            move_index = legal_count
            legal_count += 1
            try:
                if move_index == 0:
                    score = -self._negamax(
                        depth - 1,
                        -beta,
                        -alpha,
                        not is_red_turn,
                        1,
                    )
                else:
                    score = -self._negamax(
                        depth - 1,
                        -alpha - 1,
                        -alpha,
                        not is_red_turn,
                        1,
                    )
                    if alpha < score < beta:
                        self.stats.pvs_researches += 1
                        score = -self._negamax(
                            depth - 1,
                            -beta,
                            -alpha,
                            not is_red_turn,
                            1,
                        )
            finally:
                self.context.pop(undo)

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best_score, best_move

    def _negamax(self, depth, alpha, beta, is_red_turn, ply, allow_null=True):
        self.context.check_time()
        self.stats.nodes += 1

        if ply >= MAX_PLY:
            return self.context.evaluate_for_side(is_red_turn, dynamic=True)

        game_result = self.context.game_result_for_side(is_red_turn)
        if game_result is not None:
            return game_result * (MATE_SCORE - ply)
        if self.context.is_draw():
            return 0

        alpha = max(alpha, -MATE_SCORE + ply)
        beta = min(beta, MATE_SCORE - ply - 1)
        if alpha >= beta:
            return alpha

        key = self.context.state_key(is_red_turn)
        entry = self.tt.probe(key)
        tt_move = self.tt.moves[entry] if entry >= 0 else None
        if entry >= 0 and self.tt.depths[entry] >= depth:
            score = self.tt.read_score(entry, ply)
            if self.tt.flags[entry] == EXACT:
                self.stats.tt_hits += 1
                return score
            if self.tt.flags[entry] == LOWER:
                alpha = max(alpha, score)
            elif self.tt.flags[entry] == UPPER:
                beta = min(beta, score)
            if alpha >= beta:
                self.stats.tt_hits += 1
                return score

        in_check = self.context.is_in_check(is_red_turn)
        if depth <= 0:
            return self._quiescence(alpha, beta, is_red_turn, ply, in_check=in_check)

        moves = self.context.pseudo_moves(is_red_turn)
        if not moves:
            return -MATE_SCORE + ply
        if in_check:
            depth += 1

        pv_node = beta - alpha > 1
        static_eval = self.context.evaluate_for_side(is_red_turn)

        if not in_check and not pv_node:
            reverse_margin = 100 * depth
            if depth <= 2 and static_eval - reverse_margin >= beta:
                return static_eval - reverse_margin

            if (
                allow_null
                and depth >= 3
                and static_eval >= beta
                and self.context.has_non_pawn_material(is_red_turn)
            ):
                reduction = 2 + depth // 4
                score = -self._negamax(
                    depth - 1 - reduction,
                    -beta,
                    -beta + 1,
                    not is_red_turn,
                    ply + 1,
                    allow_null=False,
                )
                if score >= beta:
                    self.stats.null_cutoffs += 1
                    return beta

            razor_margin = 120 * depth
            if depth <= 2 and static_eval + razor_margin <= alpha:
                score = self._quiescence(alpha, beta, is_red_turn, ply, moves, False)
                if score <= alpha:
                    self.stats.razor_prunes += 1
                    return score

        futility_margin = (0, 100, 300, 500)
        futility_pruning = (
            not in_check
            and not pv_node
            and depth < len(futility_margin)
            and abs(alpha) < MATE_THRESHOLD
            and static_eval + futility_margin[depth] <= alpha
        )

        original_alpha = alpha
        best_move = None
        best_score = -INFINITY
        legal_count = 0
        checking_moves = self._checking_moves(moves, is_red_turn) if depth >= 3 else None
        ordered_moves = self.ordering.ordered(
            self.context.position,
            moves,
            ply,
            tt_move,
            checking_moves,
        )

        for move in ordered_moves:
            is_capture = self.context.is_capture(move)
            is_killer = self.ordering.is_killer(move, ply)
            undo = self.context.push(move)
            if undo is None:
                continue
            move_index = legal_count
            legal_count += 1
            try:
                needs_check_info = (
                    (
                        futility_pruning
                        and move_index > 0
                        and not is_capture
                    )
                    or (
                        not pv_node
                        and move_index >= 4
                        and depth >= 3
                        and not in_check
                        and not is_capture
                        and not is_killer
                    )
                )
                gives_check = (
                    self.context.is_in_check(not is_red_turn)
                    if needs_check_info
                    else False
                )

                if (
                    futility_pruning
                    and move_index > 0
                    and not is_capture
                    and not gives_check
                ):
                    self.stats.futility_prunes += 1
                    continue

                if move_index == 0:
                    score = -self._negamax(
                        depth - 1,
                        -beta,
                        -alpha,
                        not is_red_turn,
                        ply + 1,
                    )
                else:
                    reduced_depth = depth - 1
                    if (
                        not pv_node
                        and move_index >= 4
                        and depth >= 3
                        and not in_check
                        and not is_capture
                        and not gives_check
                        and not is_killer
                    ):
                        reduced_depth = max(0, depth - 2)
                        self.stats.lmr_reductions += 1

                    score = -self._negamax(
                        reduced_depth,
                        -alpha - 1,
                        -alpha,
                        not is_red_turn,
                        ply + 1,
                    )

                    if score > alpha and reduced_depth != depth - 1:
                        score = -self._negamax(
                            depth - 1,
                            -alpha - 1,
                            -alpha,
                            not is_red_turn,
                            ply + 1,
                        )

                    if alpha < score < beta:
                        self.stats.pvs_researches += 1
                        score = -self._negamax(
                            depth - 1,
                            -beta,
                            -alpha,
                            not is_red_turn,
                            ply + 1,
                        )
            finally:
                self.context.pop(undo)

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)
            if alpha >= beta:
                self.stats.beta_cutoffs += 1
                if not is_capture:
                    self.ordering.record_quiet_cutoff(
                        self.context.position, move, depth, ply
                    )
                break

        if legal_count == 0:
            return -MATE_SCORE + ply

        if best_score <= original_alpha:
            flag = UPPER
        elif best_score >= beta:
            flag = LOWER
        else:
            flag = EXACT
        self.tt.store(key, depth, best_score, flag, best_move, ply)
        return best_score

    def _quiescence(
        self,
        alpha,
        beta,
        is_red_turn,
        ply,
        moves=None,
        in_check=None,
        qply=0,
    ):
        self.context.check_time()
        self.stats.qnodes += 1

        if ply >= MAX_PLY:
            return self.context.evaluate_for_side(is_red_turn, dynamic=True)

        game_result = self.context.game_result_for_side(is_red_turn)
        if game_result is not None:
            return game_result * (MATE_SCORE - ply)
        if self.context.is_draw():
            return 0

        if in_check is None:
            in_check = self.context.is_in_check(is_red_turn)

        if qply >= MAX_QUIESCENCE_PLY and not in_check:
            return self.context.evaluate_for_side(is_red_turn, dynamic=True)

        if in_check:
            if moves is None:
                moves = self.context.pseudo_moves(is_red_turn)
            if not moves:
                return -MATE_SCORE + ply
            candidates = moves
        else:
            stand_pat = self.context.evaluate_for_side(
                is_red_turn,
                dynamic=qply == 0,
            )
            if stand_pat >= beta:
                return beta
            alpha = max(alpha, stand_pat)
            if moves is None:
                candidates = self.context.pseudo_moves(is_red_turn, captures_only=True)
            else:
                candidates = [move for move in moves if self.context.is_capture(move)]

        legal_count = 0
        for move in self.ordering.ordered(self.context.position, candidates, ply):
            attacker = self.context.piece_at_source(move)
            captured = self.context.captured_piece(move)
            if not in_check and abs(alpha) < MATE_THRESHOLD:
                captured_value = PIECE_VALUES[abs(captured)]
                if stand_pat + captured_value + 80 <= alpha:
                    continue
            undo = self.context.push(move)
            if undo is None:
                continue
            legal_count += 1
            try:
                if not in_check:
                    attacker_value = PIECE_VALUES[abs(attacker)]
                    captured_value = PIECE_VALUES[abs(captured)]
                    gives_check = self.context.is_in_check(not is_red_turn)
                    if (
                        captured_value + 100 < attacker_value
                        and not gives_check
                        and self.context.is_square_attacked(
                            *self.context.move_target(move),
                            not is_red_turn,
                        )
                    ):
                        continue
                score = -self._quiescence(
                    -beta,
                    -alpha,
                    not is_red_turn,
                    ply + 1,
                    qply=qply + 1,
                )
            finally:
                self.context.pop(undo)

            if score >= beta:
                return beta
            alpha = max(alpha, score)

        if in_check and legal_count == 0:
            return -MATE_SCORE + ply
        return alpha
