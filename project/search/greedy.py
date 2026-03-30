from __future__ import annotations

from dataclasses import dataclass

from project.board import Board, WHITE
from project.evals.base import Evaluator
from project.search.base import SearchResult, Searcher


MATE_SCORE = 100_000


def _terminal_score(board: Board) -> int | None:
    if board.is_checkmate():
        if board.stm == WHITE:
            return -MATE_SCORE
        return MATE_SCORE

    if board.draw_state():
        return 0

    return None


@dataclass(slots=True)
class GreedySearcher(Searcher):
    _name: str = "greedy"

    @property
    def name(self) -> str:
        return self._name

    def _score_after_move(self, board: Board, evaluator: Evaluator, move: int) -> int:
        board.make_move(move)

        terminal = _terminal_score(board)
        if terminal is not None:
            score = terminal
        else:
            score = evaluator.evaluate(board)

        board.unmake_move()
        return score

    def search(
        self,
        board: Board,
        evaluator: Evaluator,
        *,
        max_depth: int = 1,
        time_limit: float | None = None,
    ) -> SearchResult:
        del max_depth
        del time_limit

        moves = board.generate_legal()
        if not moves:
            terminal = _terminal_score(board)
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

        root_is_white = (board.stm == WHITE)

        best_move: int | None = None
        best_score = -1_000_000_000 if root_is_white else 1_000_000_000
        nodes = 0

        for move in moves:
            score = self._score_after_move(board, evaluator, move)
            nodes += 1

            if root_is_white:
                if score > best_score:
                    best_score = score
                    best_move = move
            else:
                if score < best_score:
                    best_score = score
                    best_move = move

        pv = [best_move] if best_move is not None else []

        return SearchResult(
            move=best_move,
            score=best_score,
            depth_reached=1,
            nodes=nodes,
            pv=pv,
            timed_out=False,
        )