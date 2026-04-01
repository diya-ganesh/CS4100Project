from __future__ import annotations

from dataclasses import dataclass, field
import time

from project.board import Board, WHITE, FLAG_CAPTURE, mv_flags
from project.evals.base import Evaluator
from project.search.base import SearchResult, Searcher


MATE_SCORE = 100_000
INF_SCORE = 1_000_000_000


def _terminal_score(board: Board, ply: int) -> int | None:
    if board.is_checkmate():
        if board.stm == WHITE:
            return -MATE_SCORE + ply
        return MATE_SCORE - ply

    if board.draw_state():
        return 0

    return None


@dataclass(slots=True)
class AlphaBetaSearcher(Searcher):
    move_order_width: int | None = None
    _name: str = "alphabeta_ids"
    _nodes: int = field(init=False, default=0)
    _deadline: float | None = field(init=False, default=None)
    _timed_out: bool = field(init=False, default=False)

    @property
    def name(self) -> str:
        return self._name

    def search(
        self,
        board: Board,
        evaluator: Evaluator,
        *,
        max_depth: int = 4,
        time_limit: float | None = None,
    ) -> SearchResult:
        self._nodes = 0
        self._timed_out = False
        self._deadline = None if time_limit is None else time.perf_counter() + time_limit

        legal = board.generate_legal()
        if not legal:
            terminal = _terminal_score(board, 0)
            if terminal is None:
                terminal = evaluator.evaluate(board)
            return SearchResult(
                move=None,
                score=terminal,
                depth_reached=0,
                nodes=1,
                pv=[],
                timed_out=False,
            )

        fallback_move = legal[0]
        fallback_score = evaluator.evaluate(board)

        best_move = fallback_move
        best_score = fallback_score
        best_pv = [best_move]
        best_depth = 0

        previous_best: int | None = None

        for depth in range(1, max_depth + 1):
            if self._time_is_up():
                break

            score, move, pv = self._root_search(
                board=board,
                evaluator=evaluator,
                depth=depth,
                previous_best=previous_best,
            )

            if self._timed_out:
                break

            if move is None:
                break

            best_move = move
            best_score = score
            best_pv = pv if pv else [move]
            best_depth = depth
            previous_best = move

        return SearchResult(
            move=best_move,
            score=best_score,
            depth_reached=best_depth,
            nodes=self._nodes,
            pv=best_pv,
            timed_out=self._timed_out,
        )

    def _time_is_up(self) -> bool:
        if self._deadline is None:
            return False
        if time.perf_counter() >= self._deadline:
            self._timed_out = True
            return True
        return False

    def _score_for_ordering(self, board: Board, evaluator: Evaluator, move: int) -> int:
        board.make_move(move)
        terminal = _terminal_score(board, 1)
        if terminal is not None:
            score = terminal
        else:
            score = evaluator.evaluate(board)
        board.unmake_move()
        return score

    def _ordered_moves(
        self,
        board: Board,
        evaluator: Evaluator,
        previous_best: int | None = None,
    ) -> list[int]:
        moves = board.generate_legal()

        if previous_best is not None and previous_best in moves:
            moves.remove(previous_best)
            moves.insert(0, previous_best)

        scored: list[tuple[int, int]] = []

        start_index = 0
        if previous_best is not None and len(moves) > 0 and moves[0] == previous_best:
            forced_score = INF_SCORE if board.stm == WHITE else -INF_SCORE
            scored.append((forced_score, previous_best))
            start_index = 1

        for move in moves[start_index:]:
            score = self._score_for_ordering(board, evaluator, move)
            scored.append((score, move))

        scored.sort(key=lambda item: item[0], reverse=(board.stm == WHITE))

        ordered = [move for _, move in scored]
        if self.move_order_width is not None:
            return ordered[:self.move_order_width]
        return ordered

    def _root_search(
        self,
        board: Board,
        evaluator: Evaluator,
        depth: int,
        previous_best: int | None,
    ) -> tuple[int, int | None, list[int]]:
        moves = self._ordered_moves(board, evaluator, previous_best=previous_best)

        if not moves:
            terminal = _terminal_score(board, 0)
            if terminal is None:
                terminal = evaluator.evaluate(board)
            return terminal, None, []

        alpha = -INF_SCORE
        beta = INF_SCORE
        best_move: int | None = None
        best_line: list[int] = []

        if board.stm == WHITE:
            best_score = -INF_SCORE

            for move in moves:
                if self._time_is_up():
                    break

                board.make_move(move)
                score, line = self._alphabeta(
                    board=board,
                    evaluator=evaluator,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    ply=1,
                )
                board.unmake_move()

                if self._timed_out:
                    break

                if score > best_score:
                    best_score = score
                    best_move = move
                    best_line = [move] + line

                if best_score > alpha:
                    alpha = best_score

                if alpha >= beta:
                    break

            return best_score, best_move, best_line

        best_score = INF_SCORE

        for move in moves:
            if self._time_is_up():
                break

            board.make_move(move)
            score, line = self._alphabeta(
                board=board,
                evaluator=evaluator,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                ply=1,
            )
            board.unmake_move()

            if self._timed_out:
                break

            if score < best_score:
                best_score = score
                best_move = move
                best_line = [move] + line

            if best_score < beta:
                beta = best_score

            if beta <= alpha:
                break

        return best_score, best_move, best_line

    def _alphabeta(
        self,
        board: Board,
        evaluator: Evaluator,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
    ) -> tuple[int, list[int]]:
        self._nodes += 1

        if self._time_is_up():
            return evaluator.evaluate(board), []

        terminal = _terminal_score(board, ply)
        if terminal is not None:
            return terminal, []

        if depth <= 0:
            # return evaluator.evaluate(board), []
            return self._quiescence(board, evaluator, alpha, beta, ply), []

        moves = self._ordered_moves(board, evaluator)

        if not moves:
            terminal = _terminal_score(board, ply)
            if terminal is not None:
                return terminal, []
            return evaluator.evaluate(board), []

        if board.stm == WHITE:
            best_score = -INF_SCORE
            best_line: list[int] = []

            for move in moves:
                board.make_move(move)
                score, line = self._alphabeta(
                    board=board,
                    evaluator=evaluator,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    ply=ply + 1,
                )
                board.unmake_move()

                if self._timed_out:
                    return evaluator.evaluate(board), best_line

                if score > best_score:
                    best_score = score
                    best_line = [move] + line

                if best_score > alpha:
                    alpha = best_score

                if alpha >= beta:
                    break

            return best_score, best_line

        best_score = INF_SCORE
        best_line: list[int] = []

        for move in moves:
            board.make_move(move)
            score, line = self._alphabeta(
                board=board,
                evaluator=evaluator,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                ply=ply + 1,
            )
            board.unmake_move()

            if self._timed_out:
                return evaluator.evaluate(board), best_line

            if score < best_score:
                best_score = score
                best_line = [move] + line

            if best_score < beta:
                beta = best_score

            if beta <= alpha:
                break

        return best_score, best_line

    def _quiescence(
        self,
        board: Board,
        evaluator: Evaluator,
        alpha: int,
        beta: int,
        ply: int,
    ) -> int:
        # baseline score for the current position
        base_score = evaluator.evaluate(board)
        if board.stm == WHITE:
            if base_score >= beta:
                return base_score
            if base_score > alpha:
                alpha = base_score
        else:
            if base_score <= alpha:
                return base_score
            if base_score < beta:
                beta = base_score
        
        best_score = base_score

        # explore capture chains 
        for move in board.generate_legal():
            if not (mv_flags(move) & FLAG_CAPTURE):
                continue
            board.make_move(move)
            score = self._quiescence(board, evaluator, alpha, beta, ply + 1)
            board.unmake_move()

            if board.stm == WHITE:
                if score > best_score:
                    best_score = score
                if score >= beta:
                    return score
                if score > alpha:
                    alpha = score
            else:
                if score < best_score:
                    best_score = score
                if score <= alpha:
                    return score
                if score < beta:
                    beta = score

        return best_score
