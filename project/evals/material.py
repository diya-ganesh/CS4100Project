from __future__ import annotations

from dataclasses import dataclass

from project.board import Board, WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK
from base import Evaluator


PIECE_VALUES = {
    WP: 100,
    WN: 320,
    WB: 330,
    WR: 500,
    WQ: 900,
    WK: 0,
    BP: 100,
    BN: 320,
    BB: 330,
    BR: 500,
    BQ: 900,
    BK: 0,
}


@dataclass(slots=True)
class MaterialEvaluator(Evaluator):
    _name: str = "material"

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, board: Board) -> int:
        score = 0

        for piece_type, bitboard in enumerate(board.bb):
            count = bitboard.bit_count()
            value = PIECE_VALUES[piece_type] * count

            if piece_type < 6:
                score += value
            else:
                score -= value

        return score