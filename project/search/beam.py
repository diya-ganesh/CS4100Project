from __future__ import annotations

from dataclasses import dataclass
import time

from project.board import Board, WHITE
from project.evals.base import Evaluator
from project.search.base import SearchResult, Searcher


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
    fen: str
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
        ok = board.make_move(move)
        if not ok:
            raise RuntimeError(
                f"BeamSearcher._score_move received illegal move "
                f"{board.move_to_uci(move)} from fen {board.fen()}"
            )

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
        root_fen = board.fen()

        ordered_root = self._ordered_moves(board, evaluator, 1)

        beam: list[_BeamNode] = []
        nodes_visited = 0

        for move in ordered_root[:self.beam_width]:
            if deadline is not None and time.perf_counter() >= deadline:
                break

            child = Board(root_fen)
            ok = child.make_move(move)
            if not ok:
                continue

            score = self._score_position(child, evaluator, 1)
            beam.append(
                _BeamNode(
                    fen=child.fen(),
                    path=(move,),
                    score=score,
                )
            )
            nodes_visited += 1

        if not beam:
            fallback = legal[0]
            fallback_score = self._score_move(board, evaluator, fallback, 1)
            return SearchResult(
                move=fallback,
                score=fallback_score,
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

            next_beam: list[_BeamNode] = []

            for node in beam:
                if deadline is not None and time.perf_counter() >= deadline:
                    timed_out = True
                    break

                current = Board(node.fen)
                next_moves = self._ordered_moves(current, evaluator, depth)
                next_moves = next_moves[:self.expand_width]

                if not next_moves:
                    leaf_score = self._score_position(current, evaluator, depth)
                    next_beam.append(
                        _BeamNode(
                            fen=current.fen(),
                            path=node.path,
                            score=leaf_score,
                        )
                    )
                    nodes_visited += 1
                    continue

                maximizing = (current.stm == WHITE)
                chosen_child: _BeamNode | None = None

                for move in next_moves:
                    if deadline is not None and time.perf_counter() >= deadline:
                        timed_out = True
                        break

                    child = Board(node.fen)
                    ok = child.make_move(move)
                    if not ok:
                        continue

                    child_score = self._score_position(child, evaluator, depth)
                    candidate = _BeamNode(
                        fen=child.fen(),
                        path=node.path + (move,),
                        score=child_score,
                    )
                    nodes_visited += 1

                    if chosen_child is None:
                        chosen_child = candidate
                    elif maximizing and candidate.score > chosen_child.score:
                        chosen_child = candidate
                    elif (not maximizing) and candidate.score < chosen_child.score:
                        chosen_child = candidate

                if timed_out:
                    break

                if chosen_child is not None:
                    next_beam.append(chosen_child)

            if timed_out:
                break

            if not next_beam:
                break

            next_beam.sort(key=lambda node: node.score, reverse=root_is_white)
            beam = next_beam[:self.beam_width]
            best = beam[0]
            depth_reached = depth

        return SearchResult(
            move=best.path[0] if best.path else legal[0],
            score=best.score,
            depth_reached=depth_reached,
            nodes=nodes_visited,
            pv=list(best.path),
            timed_out=timed_out,
        )