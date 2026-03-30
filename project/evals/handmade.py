from __future__ import annotations

from dataclasses import dataclass

from board import Board
from project.evals.base import Evaluator


@dataclass(slots=True)
class HandmadeEvaluator(Evaluator):
    _name: str = "handmade"

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, board: Board) -> int:
        return 0