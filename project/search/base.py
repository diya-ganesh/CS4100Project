from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional

from board import Board
from project.evals.base import Evaluator


@dataclass(slots=True)
class SearchResult:
    move: Optional[int]
    score: int = 0
    depth_reached: int = 0
    nodes: int = 0
    pv: list[int] = field(default_factory=list)
    timed_out: bool = False


class Searcher(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        board: Board,
        evaluator: Evaluator,
        *,
        max_depth: int = 4,
        time_limit: float | None = None,
    ) -> SearchResult:
        raise NotImplementedError