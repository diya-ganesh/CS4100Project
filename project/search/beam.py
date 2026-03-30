from __future__ import annotations

from dataclasses import dataclass
import time

from project.board import Board, WHITE
from project.evals.base import Evaluator
from base import SearchResult, Searcher



MATE_SCORE = 100_000


def _terminal_score(board: Board, ply: int) -> int | None:
    if board.is_checkmate():
        if board.stm == WHITE:
            return -MATE_SCORE + ply
        return MATE_SCORE - ply

    if board.draw_state():
        return 0

    return None


@dataclass(slots=True)
class _BeamNode:
    path: tuple[int, ...]
    score: int


@dataclass(slots=True)
class BeamSearcher(Searcher):
    beam_width: int = 16
    expand_width: int = 24
    _name: str = "beam"

    @property
    def name(self) -> str:
        return self._name

    def _score_position(self, board: Board, evaluator: Evaluator, ply: int) -> int:
        terminal = _terminal_score(board, ply)
        if terminal is not None:
            return terminal
        return evaluator.evaluate(board)

    def _score_move(self, board: Board, evaluator: Evaluator, move: int, ply: int) -> int:
        board.make_move(move)
        score = self._score_position(board, evaluator, ply)
        board.unmake_move()
        return score

    def _ordered_moves(self, board: Board, evaluator: Evaluator, ply: int) -> list[int]:
        moves = board.generate_legal()
        scored: list[tuple[int, int]] = []

        for move in moves:
            score = self._score_move(board, evaluator, move, ply)
            scored.append((score, move))

        scored.sort(key=lambda item: item[0], reverse=(board.stm == WHITE))
        return [move for _, move in scored]

    def _apply_path(self, board: Board, path: tuple[int, ...]) -> int:
        applied = 0
        for move in path:
            ok = board.make_move(move)
            if not ok:
                break
            applied += 1
        return applied

    def _undo_n(self, board: Board, count: int) -> None:
        for _ in range(count):
            board.unmake_move()

    def search(
        self,
        board: Board,
        evaluator: Evaluator,
        *,
        max_depth: int = 4,
        time_limit: float | None = None,
    ) -> SearchResult:
        start = time.perf_counter()
        deadline = None if time_limit is None else start + time_limit

        legal = board.generate_legal()
        if not legal:
            return SearchResult(
                move=None,
                score=self._score_position(board, evaluator, 0),
                depth_reached=0,
                nodes=1,
                pv=[],
                timed_out=False,
            )

        root_is_white = (board.stm == WHITE)
        ordered_root = self._ordered_moves(board, evaluator, 1)

        beam: list[_BeamNode] = []
        nodes_visited = 0

        for move in ordered_root[:self.beam_width]:
            if deadline is not None and time.perf_counter() >= deadline:
                break

            score = self._score_move(board, evaluator, move, 1)
            beam.append(_BeamNode(path=(move,), score=score))
            nodes_visited += 1

        if not beam:
            fallback = legal[0]
            return SearchResult(
                move=fallback,
                score=self._score_move(board, evaluator, fallback, 1),
                depth_reached=0,
                nodes=nodes_visited,
                pv=[fallback],
                timed_out=True,
            )

        beam.sort(key=lambda node: node.score, reverse=root_is_white)
        best = beam[0]
        depth_reached = 1
        timed_out = False

        for depth in range(2, max_depth + 1):
            if deadline is not None and time.perf_counter() >= deadline:
                timed_out = True
                break

            candidates: list[_BeamNode] = []

            for node in beam:
                if deadline is not None and time.perf_counter() >= deadline:
                    timed_out = True
                    break

                applied = self._apply_path(board, node.path)
                if applied != len(node.path):
                    self._undo_n(board, applied)
                    continue

                next_moves = self._ordered_moves(board, evaluator, depth)
                next_moves = next_moves[:self.expand_width]

                if not next_moves:
                    leaf_score = self._score_position(board, evaluator, depth)
                    candidates.append(_BeamNode(path=node.path, score=leaf_score))
                    nodes_visited += 1
                else:
                    for move in next_moves:
                        if deadline is not None and time.perf_counter() >= deadline:
                            timed_out = True
                            break

                        board.make_move(move)
                        leaf_score = self._score_position(board, evaluator, depth)
                        board.unmake_move()

                        candidates.append(_BeamNode(path=node.path + (move,), score=leaf_score))
                        nodes_visited += 1

                self._undo_n(board, applied)

                if timed_out:
                    break

            if timed_out:
                break

            if not candidates:
                break

            candidates.sort(key=lambda node: node.score, reverse=root_is_white)
            beam = candidates[:self.beam_width]

            if beam:
                best = beam[0]
                depth_reached = depth
            else:
                break

        return SearchResult(
            move=best.path[0],
            score=best.score,
            depth_reached=depth_reached,
            nodes=nodes_visited,
            pv=list(best.path),
            timed_out=timed_out,
        )