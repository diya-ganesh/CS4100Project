from __future__ import annotations

from abc import ABC, abstractmethod

from project.board import Board


class Evaluator(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, board: Board) -> int:
        raise NotImplementedError