from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from project.board import (
    Board,
    WHITE,
    BLACK,
    WP, WN, WB, WR, WQ, WK,
    BP, BN, BB, BR, BQ, BK,
    KNIGHT_ATK,
    KING_ATK,
    rook_attacks,
    bishop_attacks,
    queen_attacks,
    pop_lsb,
)
from project.evals.base import Evaluator

PAWN_PST = [
      0,   0,   0,   0,   0,   0,   0,   0,
     50,  50,  50,  50,  50,  50,  50,  50,
     10,  10,  20,  30,  30,  20,  10,  10,
      5,   5,  10,  25,  25,  10,   5,   5,
      0,   0,   0,  20,  20,   0,   0,   0,
      5,  -5, -10,   0,   0, -10,  -5,   5,
      5,  10,  10, -20, -20,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]

PAWN_PST_END = [
      0,   0,   0,   0,   0,   0,   0,   0,
     50,  50,  50,  50,  50,  50,  50,  50,
     30,  30,  30,  30,  30,  30,  30,  30,
     20,  20,  20,  20,  20,  20,  20,  20,
     10,  10,  10,  10,  10,  10,  10,  10,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_PST = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,   0,   5,   5,   0, -20, -40,
    -30,   5,  10,  15,  15,  10,   5, -30,
    -30,   0,  15,  20,  20,  15,   0, -30,
    -30,   5,  15,  20,  20,  15,   5, -30,
    -30,   0,  10,  15,  15,  10,   0, -30,
    -40, -20,   0,   0,   0,   0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]

KNIGHT_PST_END = [
    -10,  -5,  -5,  -5,  -5,  -5,  -5, -10,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,  15,  15,  15,  15,   0,  -5,
     -5,   0,  15,  15,  15,  15,   0,  -5,
     -5,   0,  15,  15,  15,  15,   0,  -5,
     -5,   0,  10,  15,  15,  10,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
    -10,  -5,  -5,  -5,  -5,  -5,  -5, -10,
]

BISHOP_PST = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,   5,   0,   0,   0,   0,   5, -10,
    -10,  10,  10,  10,  10,  10,  10, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,   5,  10,  10,   5,   5, -10,
    -10,   0,   5,  10,  10,   5,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]

BISHOP_PST_END = [
    -15, -10, -10, -10, -10, -10, -10, -15,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   5,  10,  15,  15,  10,   5, -10,
    -10,   5,  10,  15,  15,  10,   5, -10,
    -10,   0,  10,  10,  10,  10,   0, -10,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -15, -10, -10, -10, -10, -10, -10, -15,
]

ROOK_PST = [
      0,   0,   0,   5,   5,   0,   0,   0,
     10,  20,  20,  20,  20,  20,  20,  10,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]

ROOK_PST_END = [
      0,   0,   0,  10,  10,   0,   0,   0,
     10,  20,  20,  20,  20,  20,  20,  10,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
      0,   0,   0,   0,   0,   0,   0,   0,
      5,   5,   5,  10,  10,   5,   5,   5,
]

QUEEN_PST = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   0,   0, -10,
    -10,   0,   5,   5,   5,   5,   0, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]

QUEEN_PST_END = [
    -10,  -5,  -5,  -5,  -5,  -5,  -5, -10,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,  10,  10,  10,  10,   0,  -5,
     -5,   5,  10,  15,  15,  10,   5,  -5,
     -5,   5,  10,  15,  15,  10,   5,  -5,
     -5,   0,  10,  10,  10,  10,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
    -10,  -5,  -5,  -5,  -5,  -5,  -5, -10,
]

KING_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20,
]

KING_PST_END = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50,
]

MG_VALUE = {
    WP: 100, WN: 325, WB: 335, WR: 500, WQ: 975, WK: 0,
    BP: 100, BN: 325, BB: 335, BR: 500, BQ: 975, BK: 0,
}

EG_VALUE = {
    WP: 120, WN: 300, WB: 320, WR: 510, WQ: 940, WK: 0,
    BP: 120, BN: 300, BB: 320, BR: 510, BQ: 940, BK: 0,
}

PST_MG = {
    WP: PAWN_PST,
    WN: KNIGHT_PST,
    WB: BISHOP_PST,
    WR: ROOK_PST,
    WQ: QUEEN_PST,
    WK: KING_PST,
    BP: PAWN_PST,
    BN: KNIGHT_PST,
    BB: BISHOP_PST,
    BR: ROOK_PST,
    BQ: QUEEN_PST,
    BK: KING_PST,
}

PST_EG = {
    WP: PAWN_PST_END,
    WN: KNIGHT_PST_END,
    WB: BISHOP_PST_END,
    WR: ROOK_PST_END,
    WQ: QUEEN_PST_END,
    WK: KING_PST_END,
    BP: PAWN_PST_END,
    BN: KNIGHT_PST_END,
    BB: BISHOP_PST_END,
    BR: ROOK_PST_END,
    BQ: QUEEN_PST_END,
    BK: KING_PST_END,
}

FILE_MASKS = [0x0101010101010101 << f for f in range(8)]
RANK_MASKS = [0xFF << (8 * r) for r in range(8)]
CENTER_MASK = (1 << 27) | (1 << 28) | (1 << 35) | (1 << 36)
EXT_CENTER_MASK = (
    (1 << 18) | (1 << 19) | (1 << 20) | (1 << 21) |
    (1 << 26) | (1 << 27) | (1 << 28) | (1 << 29) |
    (1 << 34) | (1 << 35) | (1 << 36) | (1 << 37) |
    (1 << 42) | (1 << 43) | (1 << 44) | (1 << 45)
)
WHITE_KINGSIDE_SHELTER = (1 << 13) | (1 << 14) | (1 << 15) | (1 << 21) | (1 << 22) | (1 << 23)
WHITE_QUEENSIDE_SHELTER = (1 << 8) | (1 << 9) | (1 << 10) | (1 << 16) | (1 << 17) | (1 << 18)
BLACK_KINGSIDE_SHELTER = (1 << 53) | (1 << 54) | (1 << 55) | (1 << 45) | (1 << 46) | (1 << 47)
BLACK_QUEENSIDE_SHELTER = (1 << 48) | (1 << 49) | (1 << 50) | (1 << 40) | (1 << 41) | (1 << 42)


def mirror_sq(sq: int) -> int:
    return sq ^ 56


def file_of(sq: int) -> int:
    return sq & 7


def rank_of(sq: int) -> int:
    return sq >> 3


def manhattan(a: int, b: int) -> int:
    return abs(file_of(a) - file_of(b)) + abs(rank_of(a) - rank_of(b))


def square_color(sq: int) -> int:
    return (file_of(sq) + rank_of(sq)) & 1


def piece_bb(board: Board, piece: int) -> int:
    return board.bb[piece]


def side_pawns(board: Board, color: int) -> int:
    return board.bb[WP if color == WHITE else BP]


def side_knights(board: Board, color: int) -> int:
    return board.bb[WN if color == WHITE else BN]


def side_bishops(board: Board, color: int) -> int:
    return board.bb[WB if color == WHITE else BB]


def side_rooks(board: Board, color: int) -> int:
    return board.bb[WR if color == WHITE else BR]


def side_queens(board: Board, color: int) -> int:
    return board.bb[WQ if color == WHITE else BQ]


def side_king(board: Board, color: int) -> int:
    return board.bb[WK if color == WHITE else BK]


def rank_relative(color: int, sq: int) -> int:
    r = rank_of(sq)
    return r if color == WHITE else 7 - r


def iter_bits(bb: int):
    while bb:
        sq, bb = pop_lsb(bb)
        yield sq

def _has_bit(bb: int, sq: int) -> bool:
    return 0 <= sq < 64 and bool(bb & (1 << sq))


FILE_A = FILE_MASKS[0]
FILE_H = FILE_MASKS[7]
NOT_FILE_A = ((1 << 64) - 1) ^ FILE_A
NOT_FILE_H = ((1 << 64) - 1) ^ FILE_H

WHITE_PIECES = (WP, WN, WB, WR, WQ, WK)
BLACK_PIECES = (BP, BN, BB, BR, BQ, BK)

PIECE_VALUES_MG = {
    WP: 100, WN: 325, WB: 340, WR: 505, WQ: 980, WK: 0,
    BP: 100, BN: 325, BB: 340, BR: 505, BQ: 980, BK: 0,
}
PIECE_VALUES_EG = {
    WP: 120, WN: 305, WB: 330, WR: 515, WQ: 945, WK: 0,
    BP: 120, BN: 305, BB: 330, BR: 515, BQ: 945, BK: 0,
}

THREAT_BY_PIECE_MG = {
    WP: 0, WN: 14, WB: 16, WR: 26, WQ: 38, WK: 0,
    BP: 0, BN: 14, BB: 16, BR: 26, BQ: 38, BK: 0,
}
THREAT_BY_PIECE_EG = {
    WP: 0, WN: 10, WB: 12, WR: 22, WQ: 28, WK: 0,
    BP: 0, BN: 10, BB: 12, BR: 22, BQ: 28, BK: 0,
}
HANGING_BY_PIECE_MG = {
    WP: 7, WN: 28, WB: 30, WR: 48, WQ: 72, WK: 0,
    BP: 7, BN: 28, BB: 30, BR: 48, BQ: 72, BK: 0,
}
HANGING_BY_PIECE_EG = {
    WP: 8, WN: 22, WB: 24, WR: 38, WQ: 56, WK: 0,
    BP: 8, BN: 22, BB: 24, BR: 38, BQ: 56, BK: 0,
}


def pawn_attacks_bb(pawns: int, color: int) -> int:
    if color == WHITE:
        return ((pawns << 7) & NOT_FILE_H) | ((pawns << 9) & NOT_FILE_A)
    return ((pawns >> 7) & NOT_FILE_A) | ((pawns >> 9) & NOT_FILE_H)


def attacks_from_piece(board: Board, piece: int, sq: int, occ: int) -> int:
    if piece in (WP, BP):
        return pawn_attacks_bb(1 << sq, WHITE if piece == WP else BLACK)
    if piece in (WN, BN):
        return KNIGHT_ATK[sq]
    if piece in (WB, BB):
        return bishop_attacks(sq, occ)
    if piece in (WR, BR):
        return rook_attacks(sq, occ)
    if piece in (WQ, BQ):
        return queen_attacks(sq, occ)
    return KING_ATK[sq]


def side_attack_map(board: Board, color: int, occ: int | None = None) -> int:
    occ = board.occ_all if occ is None else occ
    attacks = pawn_attacks_bb(side_pawns(board, color), color)

    for sq in iter_bits(side_knights(board, color)):
        attacks |= KNIGHT_ATK[sq]
    for sq in iter_bits(side_bishops(board, color)):
        attacks |= bishop_attacks(sq, occ)
    for sq in iter_bits(side_rooks(board, color)):
        attacks |= rook_attacks(sq, occ)
    for sq in iter_bits(side_queens(board, color)):
        attacks |= queen_attacks(sq, occ)

    kingbb = side_king(board, color)
    if kingbb:
        king_sq, _ = pop_lsb(kingbb)
        attacks |= KING_ATK[king_sq]
    return attacks


def central_distance(sq: int) -> int:
    return abs(file_of(sq) - 3) + abs(rank_of(sq) - 3)


@dataclass(slots=True)
class HandmadeEvaluator(Evaluator):
    _name: str = "handmade"

    bishop_pair_bonus_mg: int = 38
    bishop_pair_bonus_eg: int = 58

    rook_open_file_mg: int = 24
    rook_open_file_eg: int = 18
    rook_semi_open_file_mg: int = 14
    rook_semi_open_file_eg: int = 10
    rook_on_seventh_mg: int = 26
    rook_on_seventh_eg: int = 22
    rook_behind_passer_mg: int = 16
    rook_behind_passer_eg: int = 28
    rook_trapped_by_king_mg: int = 20

    knight_outpost_mg: int = 24
    knight_outpost_eg: int = 14
    bishop_outpost_mg: int = 12
    bishop_outpost_eg: int = 10
    knight_rim_penalty_mg: int = 12
    bishop_bad_pawn_mg: int = 4

    queen_early_penalty_mg: int = 12
    queen_harass_bonus_mg: int = 16
    queen_harass_bonus_eg: int = 10

    isolated_pawn_mg: int = 14
    isolated_pawn_eg: int = 12
    doubled_pawn_mg: int = 10
    doubled_pawn_eg: int = 14
    backward_pawn_mg: int = 11
    backward_pawn_eg: int = 10
    pawn_island_penalty_mg: int = 6
    pawn_island_penalty_eg: int = 5
    connected_pawn_bonus_mg: int = 8
    connected_pawn_bonus_eg: int = 10
    pawn_phalanx_bonus_mg: int = 5
    pawn_phalanx_bonus_eg: int = 7
    candidate_passer_bonus_mg: int = 8
    candidate_passer_bonus_eg: int = 14
    passed_rank_bonus_mg: tuple[int, ...] = (0, 5, 10, 18, 32, 55, 95, 0)
    passed_rank_bonus_eg: tuple[int, ...] = (0, 12, 22, 40, 70, 110, 170, 0)
    protected_passer_bonus_mg: int = 12
    protected_passer_bonus_eg: int = 22
    connected_passers_bonus_mg: int = 12
    connected_passers_bonus_eg: int = 26
    blockaded_passer_penalty_mg: int = 14
    blockaded_passer_penalty_eg: int = 22

    mobility_weights_mg: tuple[int, int, int, int] = (4, 5, 3, 2)
    mobility_weights_eg: tuple[int, int, int, int] = (4, 5, 4, 2)

    center_control_mg: int = 4
    center_control_eg: int = 2
    extended_center_control_mg: int = 1
    connectivity_bonus_mg: int = 4
    connectivity_bonus_eg: int = 3

    king_file_shelter_mg: int = 9
    king_file_shelter_eg: int = 2
    king_open_file_penalty_mg: int = 18
    king_half_open_file_penalty_mg: int = 10
    king_storm_penalty_mg: int = 12
    king_center_penalty_mg: int = 20
    king_attacked_ring_mg: int = 6
    king_undefended_ring_mg: int = 8
    king_attacker_bonus_mg: int = 8

    hanging_bonus_scale_mg: int = 1
    hanging_bonus_scale_eg: int = 1
    attack_pressure_scale_mg: int = 1
    attack_pressure_scale_eg: int = 1

    space_bonus_mg: int = 3
    space_bonus_eg: int = 0
    safe_space_bonus_mg: int = 4

    tempo_bonus_mg: int = 12
    tempo_bonus_eg: int = 6

    lazy_margin: int = 260
    max_cache_size: int = 200000
    _eval_cache: Dict[int, int] = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self._name

    def evaluate(self, board: Board) -> int:
        if board.is_checkmate():
            return -100000 if board.stm == WHITE else 100000
        if board.draw_state():
            return 0

        cached = self._eval_cache.get(board.hash)
        if cached is not None:
            return cached

        phase = self._game_phase(board)
        quick_mg, quick_eg = self._material_and_pst(board)
        quick = self._taper(quick_mg, quick_eg, phase)
        quick += self._tempo_bonus(phase) * (1 if board.stm == WHITE else -1)

        if abs(quick) >= self.lazy_margin and phase >= 12:
            self._store(board.hash, quick)
            return quick

        white_mg = 0
        white_eg = 0
        black_mg = 0
        black_eg = 0

        white_mg += self._material_and_pst_side(board, WHITE, opening=True)
        white_eg += self._material_and_pst_side(board, WHITE, opening=False)
        black_mg += self._material_and_pst_side(board, BLACK, opening=True)
        black_eg += self._material_and_pst_side(board, BLACK, opening=False)

        pwmg, pweg = self._pawn_structure(board, WHITE)
        pbmg, pbeg = self._pawn_structure(board, BLACK)
        white_mg += pwmg
        white_eg += pweg
        black_mg += pbmg
        black_eg += pbeg

        wamap = side_attack_map(board, WHITE)
        bamap = side_attack_map(board, BLACK)

        pmg, peg = self._piece_activity(board, WHITE)
        bmg, beg = self._piece_activity(board, BLACK)
        white_mg += pmg
        white_eg += peg
        black_mg += bmg
        black_eg += beg

        mmg, meg = self._mobility(board, WHITE, bamap)
        bmmg, bmeg = self._mobility(board, BLACK, wamap)
        white_mg += mmg
        white_eg += meg
        black_mg += bmmg
        black_eg += bmeg

        cmg, ceg = self._center_control(board, WHITE)
        bcmg, bceg = self._center_control(board, BLACK)
        white_mg += cmg
        white_eg += ceg
        black_mg += bcmg
        black_eg += bceg

        conmg, coneg = self._connectivity(board, WHITE)
        bconmg, bconeg = self._connectivity(board, BLACK)
        white_mg += conmg
        white_eg += coneg
        black_mg += bconmg
        black_eg += bconeg

        tmg, teg = self._threats(board, WHITE)
        btmg, bteg = self._threats(board, BLACK)
        white_mg += tmg
        white_eg += teg
        black_mg += btmg
        black_eg += bteg

        ksmg, kseg = self._king_safety(board, WHITE, phase, bamap, wamap)
        bksmg, bkseg = self._king_safety(board, BLACK, phase, wamap, bamap)
        white_mg += ksmg
        white_eg += kseg
        black_mg += bksmg
        black_eg += bkseg

        spmg, speg = self._space(board, WHITE, bamap)
        bspmg, bspeg = self._space(board, BLACK, wamap)
        white_mg += spmg
        white_eg += speg
        black_mg += bspmg
        black_eg += bspeg

        oqmg, oqeg = self._opening_queen_penalty(board, WHITE)
        boqmg, boqeg = self._opening_queen_penalty(board, BLACK)
        white_mg += oqmg
        white_eg += oqeg
        black_mg += boqmg
        black_eg += boqeg

        mpmg, mpeg = self._mopup(board, WHITE, phase)
        bmpmg, bmpeg = self._mopup(board, BLACK, phase)
        white_mg += mpmg
        white_eg += mpeg
        black_mg += bmpmg
        black_eg += bmpeg

        mg = self._analog_compress(white_mg - black_mg)
        eg = self._analog_compress(white_eg - black_eg)

        score = self._taper(mg, eg, phase)
        score += self._tempo_bonus(phase) * (1 if board.stm == WHITE else -1)
        score = self._endgame_scale(board, score, phase)

        self._store(board.hash, score)
        return score

    def _store(self, key: int, value: int) -> None:
        if len(self._eval_cache) > self.max_cache_size:
            self._eval_cache.clear()
        self._eval_cache[key] = value

    def _game_phase(self, board: Board) -> int:
        phase = 0
        phase += (board.bb[WN].bit_count() + board.bb[BN].bit_count()) * 1
        phase += (board.bb[WB].bit_count() + board.bb[BB].bit_count()) * 1
        phase += (board.bb[WR].bit_count() + board.bb[BR].bit_count()) * 2
        phase += (board.bb[WQ].bit_count() + board.bb[BQ].bit_count()) * 4
        return max(0, min(24, phase))

    def _taper(self, mg: int, eg: int, phase: int) -> int:
        return (mg * phase + eg * (24 - phase)) // 24

    def _tempo_bonus(self, phase: int) -> int:
        return self._taper(self.tempo_bonus_mg, self.tempo_bonus_eg, phase)

    def _analog_compress(self, score: int) -> int:
        if score > 0:
            return score - (score // 32)
        if score < 0:
            return score + ((-score) // 32)
        return 0

    def _material_and_pst(self, board: Board) -> tuple[int, int]:
        white_mg = self._material_and_pst_side(board, WHITE, opening=True)
        white_eg = self._material_and_pst_side(board, WHITE, opening=False)
        black_mg = self._material_and_pst_side(board, BLACK, opening=True)
        black_eg = self._material_and_pst_side(board, BLACK, opening=False)
        return white_mg - black_mg, white_eg - black_eg

    def _material_and_pst_side(self, board: Board, color: int, opening: bool) -> int:
        score = 0
        tables = PST_MG if opening else PST_EG
        values = MG_VALUE if opening else EG_VALUE
        pieces = WHITE_PIECES if color == WHITE else BLACK_PIECES

        for p in pieces:
            bbp = board.bb[p]
            while bbp:
                sq, bbp = pop_lsb(bbp)
                tsq = sq if color == WHITE else mirror_sq(sq)
                score += values[p]
                score += tables[p][tsq]

        bishops = side_bishops(board, color)
        if bishops.bit_count() >= 2:
            score += self.bishop_pair_bonus_mg if opening else self.bishop_pair_bonus_eg

        return score

    def _non_pawn_material(self, board: Board, color: int) -> int:
        if color == WHITE:
            return (
                board.bb[WN].bit_count() * PIECE_VALUES_MG[WN] +
                board.bb[WB].bit_count() * PIECE_VALUES_MG[WB] +
                board.bb[WR].bit_count() * PIECE_VALUES_MG[WR] +
                board.bb[WQ].bit_count() * PIECE_VALUES_MG[WQ]
            )
        return (
            board.bb[BN].bit_count() * PIECE_VALUES_MG[BN] +
            board.bb[BB].bit_count() * PIECE_VALUES_MG[BB] +
            board.bb[BR].bit_count() * PIECE_VALUES_MG[BR] +
            board.bb[BQ].bit_count() * PIECE_VALUES_MG[BQ]
        )

    def _pawn_structure(self, board: Board, color: int) -> tuple[int, int]:
        pawns = side_pawns(board, color)
        enemy_pawns = side_pawns(board, color ^ 1)

        mg = 0
        eg = 0

        islands = 0
        prev_filled = False
        for f in range(8):
            cnt = (pawns & FILE_MASKS[f]).bit_count()
            filled = cnt > 0
            if filled and not prev_filled:
                islands += 1
            prev_filled = filled
            if cnt > 1:
                mg -= (cnt - 1) * self.doubled_pawn_mg
                eg -= (cnt - 1) * self.doubled_pawn_eg
        if islands > 1:
            mg -= (islands - 1) * self.pawn_island_penalty_mg
            eg -= (islands - 1) * self.pawn_island_penalty_eg

        pawn_squares = list(iter_bits(pawns))
        passed = set()

        for sq in pawn_squares:
            f = file_of(sq)
            rrel = rank_relative(color, sq)

            same_rank_adjacent = False
            if f > 0 and _has_bit(pawns, sq - 1):
                same_rank_adjacent = True
            if f < 7 and _has_bit(pawns, sq + 1):
                same_rank_adjacent = True

            supported = self._is_pawn_protected(board, color, sq)
            connected = supported or same_rank_adjacent

            has_left = f > 0 and (pawns & FILE_MASKS[f - 1]) != 0
            has_right = f < 7 and (pawns & FILE_MASKS[f + 1]) != 0
            isolated = not has_left and not has_right
            if isolated:
                mg -= self.isolated_pawn_mg
                eg -= self.isolated_pawn_eg

            if connected:
                mg += self.connected_pawn_bonus_mg
                eg += self.connected_pawn_bonus_eg
                if same_rank_adjacent:
                    mg += self.pawn_phalanx_bonus_mg
                    eg += self.pawn_phalanx_bonus_eg
            elif not isolated and self._is_backward_pawn(board, color, sq):
                mg -= self.backward_pawn_mg
                eg -= self.backward_pawn_eg

            if self._is_passed_pawn(color, sq, enemy_pawns):
                passed.add(sq)
                mg += self.passed_rank_bonus_mg[rrel]
                eg += self.passed_rank_bonus_eg[rrel]

                if supported:
                    mg += self.protected_passer_bonus_mg
                    eg += self.protected_passer_bonus_eg

                if self._has_adjacent_friendly_pawn(pawns, sq):
                    mg += self.connected_passers_bonus_mg
                    eg += self.connected_passers_bonus_eg

                front = sq + 8 if color == WHITE else sq - 8
                if 0 <= front < 64 and (board.occ_all & (1 << front)):
                    mg -= self.blockaded_passer_penalty_mg
                    eg -= self.blockaded_passer_penalty_eg
                else:
                    enemy_king_sq = board.king_sq(color ^ 1)
                    own_king_sq = board.king_sq(color)
                    if enemy_king_sq != -1 and own_king_sq != -1:
                        eg += max(0, 7 - manhattan(front if 0 <= front < 64 else sq, enemy_king_sq)) * 3
                        eg += max(0, 6 - manhattan(sq, own_king_sq)) * 2
            elif self._is_candidate_passer(board, color, sq):
                mg += self.candidate_passer_bonus_mg * max(0, rrel - 1)
                eg += self.candidate_passer_bonus_eg * max(0, rrel - 1)

        return mg, eg

    def _is_candidate_passer(self, board: Board, color: int, sq: int) -> bool:
        f = file_of(sq)
        pawns = side_pawns(board, color)
        enemy_pawns = side_pawns(board, color ^ 1)

        if self._is_passed_pawn(color, sq, enemy_pawns):
            return False

        front_mask = 0
        r = rank_of(sq)
        if color == WHITE:
            for rr in range(r + 1, 8):
                front_mask |= 1 << (rr * 8 + f)
        else:
            for rr in range(0, r):
                front_mask |= 1 << (rr * 8 + f)
        if enemy_pawns & front_mask:
            return False

        friends = 0
        enemies = 0
        for ff in (f - 1, f + 1):
            if not 0 <= ff < 8:
                continue
            if color == WHITE:
                for rr in range(r, 8):
                    bit = 1 << (rr * 8 + ff)
                    if pawns & bit:
                        friends += 1
                    if enemy_pawns & bit:
                        enemies += 1
            else:
                for rr in range(r, -1, -1):
                    bit = 1 << (rr * 8 + ff)
                    if pawns & bit:
                        friends += 1
                    if enemy_pawns & bit:
                        enemies += 1
        return friends >= enemies

    def _has_adjacent_friendly_pawn(self, pawns: int, sq: int) -> bool:
        f = file_of(sq)
        for df in (-1, 1):
            ff = f + df
            if 0 <= ff < 8:
                for dr in (-1, 0, 1):
                    rr = rank_of(sq) + dr
                    if 0 <= rr < 8 and _has_bit(pawns, rr * 8 + ff):
                        return True
        return False

    def _is_backward_pawn(self, board: Board, color: int, sq: int) -> bool:
        f = file_of(sq)
        r = rank_of(sq)
        pawns = side_pawns(board, color)

        if color == WHITE:
            support = 0
            if f > 0:
                for rr in range(r - 1, -1, -1):
                    support |= 1 << (rr * 8 + (f - 1))
            if f < 7:
                for rr in range(r - 1, -1, -1):
                    support |= 1 << (rr * 8 + (f + 1))
            if pawns & support:
                return False
            front = sq + 8
            return front < 64 and bool(board.attacks_to(front, BLACK)) and not bool(board.attacks_to(front, WHITE))

        support = 0
        if f > 0:
            for rr in range(r + 1, 8):
                support |= 1 << (rr * 8 + (f - 1))
        if f < 7:
            for rr in range(r + 1, 8):
                support |= 1 << (rr * 8 + (f + 1))
        if pawns & support:
            return False
        front = sq - 8
        return front >= 0 and bool(board.attacks_to(front, WHITE)) and not bool(board.attacks_to(front, BLACK))

    def _is_passed_pawn(self, color: int, sq: int, enemy_pawns: int) -> bool:
        f = file_of(sq)
        r = rank_of(sq)
        mask = 0
        files = [f]
        if f > 0:
            files.append(f - 1)
        if f < 7:
            files.append(f + 1)

        if color == WHITE:
            for ff in files:
                for rr in range(r + 1, 8):
                    mask |= 1 << (rr * 8 + ff)
        else:
            for ff in files:
                for rr in range(0, r):
                    mask |= 1 << (rr * 8 + ff)

        return (enemy_pawns & mask) == 0

    def _is_pawn_protected(self, board: Board, color: int, sq: int) -> bool:
        pawns = side_pawns(board, color)
        f = file_of(sq)
        if color == WHITE:
            return ((f > 0 and sq >= 9 and (pawns & (1 << (sq - 9)))) or
                    (f < 7 and sq >= 7 and (pawns & (1 << (sq - 7)))))
        return ((f > 0 and sq <= 55 and (pawns & (1 << (sq + 7)))) or
                (f < 7 and sq <= 54 and (pawns & (1 << (sq + 9)))))

    def _piece_activity(self, board: Board, color: int) -> tuple[int, int]:
        mg = 0
        eg = 0

        pawns = side_pawns(board, color)
        enemy_pawns = side_pawns(board, color ^ 1)
        occ = board.occ_all
        passed = self._passed_pawn_squares(board, color)

        for sq in iter_bits(side_knights(board, color)):
            if self._is_outpost(board, color, sq):
                mg += self.knight_outpost_mg
                eg += self.knight_outpost_eg
            if file_of(sq) in (0, 7):
                mg -= self.knight_rim_penalty_mg
            mg += max(0, 6 - central_distance(sq)) * 2
            eg += max(0, 6 - central_distance(sq))

        bishop_sqs = list(iter_bits(side_bishops(board, color)))
        for sq in bishop_sqs:
            if self._is_outpost(board, color, sq):
                mg += self.bishop_outpost_mg
                eg += self.bishop_outpost_eg

            same_color_pawns = 0
            for psq in iter_bits(pawns):
                if square_color(psq) == square_color(sq):
                    same_color_pawns += 1
            mg -= same_color_pawns * self.bishop_bad_pawn_mg

            attack_mask = bishop_attacks(sq, occ)
            if attack_mask & CENTER_MASK:
                mg += 8
                eg += 5
            if attack_mask & EXT_CENTER_MASK:
                mg += 4

            if color == WHITE:
                if sq == 48 and (board.bb[BP] & (1 << 41)):
                    mg -= 28
                    eg -= 18
                if sq == 55 and (board.bb[BP] & (1 << 46)):
                    mg -= 28
                    eg -= 18
            else:
                if sq == 8 and (board.bb[WP] & (1 << 17)):
                    mg -= 28
                    eg -= 18
                if sq == 15 and (board.bb[WP] & (1 << 22)):
                    mg -= 28
                    eg -= 18

        rooks = list(iter_bits(side_rooks(board, color)))
        for sq in rooks:
            f = file_of(sq)
            own_file_pawns = pawns & FILE_MASKS[f]
            enemy_file_pawns = enemy_pawns & FILE_MASKS[f]

            if own_file_pawns == 0 and enemy_file_pawns == 0:
                mg += self.rook_open_file_mg
                eg += self.rook_open_file_eg
            elif own_file_pawns == 0:
                mg += self.rook_semi_open_file_mg
                eg += self.rook_semi_open_file_eg

            if rank_relative(color, sq) == 6:
                mg += self.rook_on_seventh_mg
                eg += self.rook_on_seventh_eg

            for psq in passed:
                same_file = file_of(psq) == f
                if not same_file:
                    continue
                if color == WHITE and sq < psq:
                    mg += self.rook_behind_passer_mg
                    eg += self.rook_behind_passer_eg
                if color == BLACK and sq > psq:
                    mg += self.rook_behind_passer_mg
                    eg += self.rook_behind_passer_eg

            king_sq = board.king_sq(color)
            if king_sq != -1 and rank_of(sq) == rank_of(king_sq):
                if (file_of(king_sq) < 4 and file_of(sq) < file_of(king_sq)) or (
                    file_of(king_sq) > 3 and file_of(sq) > file_of(king_sq)
                ):
                    if rook_attacks(sq, occ).bit_count() <= 3:
                        mg -= self.rook_trapped_by_king_mg

        if len(rooks) >= 2:
            a, b = rooks[0], rooks[1]
            if rank_of(a) == rank_of(b) or file_of(a) == file_of(b):
                occ_between = self._between_mask(a, b) & board.occ_all
                if occ_between == 0:
                    mg += 18
                    eg += 12

        queens = list(iter_bits(side_queens(board, color)))
        for sq in queens:
            mg += max(0, 5 - central_distance(sq))
            eg += max(0, 6 - central_distance(sq))

        return mg, eg

    def _passed_pawn_squares(self, board: Board, color: int) -> list[int]:
        enemy_pawns = side_pawns(board, color ^ 1)
        return [sq for sq in iter_bits(side_pawns(board, color)) if self._is_passed_pawn(color, sq, enemy_pawns)]

    def _is_outpost(self, board: Board, color: int, sq: int) -> bool:
        if color == WHITE:
            if rank_of(sq) < 3:
                return False
        else:
            if rank_of(sq) > 4:
                return False

        f = file_of(sq)
        enemy_pawns = side_pawns(board, color ^ 1)
        chase_mask = 0

        if color == WHITE:
            if f > 0:
                for rr in range(rank_of(sq), 8):
                    chase_mask |= 1 << (rr * 8 + (f - 1))
            if f < 7:
                for rr in range(rank_of(sq), 8):
                    chase_mask |= 1 << (rr * 8 + (f + 1))
        else:
            if f > 0:
                for rr in range(0, rank_of(sq) + 1):
                    chase_mask |= 1 << (rr * 8 + (f - 1))
            if f < 7:
                for rr in range(0, rank_of(sq) + 1):
                    chase_mask |= 1 << (rr * 8 + (f + 1))

        if enemy_pawns & chase_mask:
            return False

        return self._is_pawn_protected(board, color, sq)

    def _between_mask(self, a: int, b: int) -> int:
        mask = 0
        af, ar = file_of(a), rank_of(a)
        bf, br = file_of(b), rank_of(b)
        df = (bf > af) - (bf < af)
        dr = (br > ar) - (br < ar)

        if df == 0 and dr == 0:
            return 0
        if not (df == 0 or dr == 0 or abs(bf - af) == abs(br - ar)):
            return 0

        cf, cr = af + df, ar + dr
        while cf != bf or cr != br:
            mask |= 1 << (cr * 8 + cf)
            cf += df
            cr += dr

        mask &= ~(1 << a)
        mask &= ~(1 << b)
        return mask

    def _mobility(self, board: Board, color: int, enemy_attack_map: int) -> tuple[int, int]:
        mg = 0
        eg = 0
        own_occ = board.occ[color]
        occ = board.occ_all
        enemy_pawn_danger = pawn_attacks_bb(side_pawns(board, color ^ 1), color ^ 1)

        for sq in iter_bits(side_knights(board, color)):
            att = KNIGHT_ATK[sq] & ~own_occ
            safe = att & ~enemy_pawn_danger
            m = safe.bit_count()
            mg += m * self.mobility_weights_mg[0]
            eg += att.bit_count() * self.mobility_weights_eg[0]
            if m <= 2:
                mg -= 10
                eg -= 6

        for sq in iter_bits(side_bishops(board, color)):
            att = bishop_attacks(sq, occ) & ~own_occ
            safe = att & ~enemy_pawn_danger
            mg += safe.bit_count() * self.mobility_weights_mg[1]
            eg += att.bit_count() * self.mobility_weights_eg[1]
            if safe.bit_count() <= 3:
                mg -= 8

        for sq in iter_bits(side_rooks(board, color)):
            att = rook_attacks(sq, occ) & ~own_occ
            mg += att.bit_count() * self.mobility_weights_mg[2]
            eg += att.bit_count() * self.mobility_weights_eg[2]

        for sq in iter_bits(side_queens(board, color)):
            att = queen_attacks(sq, occ) & ~own_occ
            safe = att & ~enemy_attack_map
            mg += safe.bit_count() * self.mobility_weights_mg[3]
            eg += att.bit_count() * self.mobility_weights_eg[3]

        return mg, eg

    def _center_control(self, board: Board, color: int) -> tuple[int, int]:
        mg = 0
        eg = 0

        for sq in (27, 28, 35, 36):
            attackers = board.attacks_to(sq, color).bit_count()
            mg += attackers * self.center_control_mg
            eg += attackers * self.center_control_eg

        ext = EXT_CENTER_MASK & ~CENTER_MASK
        for sq in iter_bits(ext):
            attackers = board.attacks_to(sq, color).bit_count()
            mg += attackers * self.extended_center_control_mg
            eg += attackers

        occ = board.occ[color]
        mg += (occ & CENTER_MASK).bit_count() * 10
        eg += (occ & CENTER_MASK).bit_count() * 4
        mg += (occ & ext).bit_count() * 3

        return mg, eg

    def _connectivity(self, board: Board, color: int) -> tuple[int, int]:
        mg = 0
        eg = 0
        own_occ = board.occ[color]

        defended = 0
        pawn_defended = 0
        pawns = side_pawns(board, color)
        pawn_attacks = pawn_attacks_bb(pawns, color)

        for sq in iter_bits(own_occ):
            if board.attacks_to(sq, color):
                defended += 1
            if pawn_attacks & (1 << sq):
                pawn_defended += 1

        mg += defended * self.connectivity_bonus_mg
        eg += defended * self.connectivity_bonus_eg
        mg += pawn_defended * 2
        eg += pawn_defended

        return mg, eg

    def _threats(self, board: Board, color: int) -> tuple[int, int]:
        mg = 0
        eg = 0

        enemy = color ^ 1
        own_pawns = side_pawns(board, color)
        own_minors = side_knights(board, color) | side_bishops(board, color)
        own_rooks = side_rooks(board, color)

        enemy_piece_groups = BLACK_PIECES if color == WHITE else WHITE_PIECES
        for p in enemy_piece_groups:
            if p in (WK, BK):
                continue
            for sq in iter_bits(board.bb[p]):
                attackers_bb = board.attacks_to(sq, color)
                if not attackers_bb:
                    continue
                defenders = board.attacks_to(sq, enemy).bit_count()

                if attackers_bb & own_pawns:
                    mg += THREAT_BY_PIECE_MG[p]
                    eg += THREAT_BY_PIECE_EG[p]

                if defenders == 0:
                    mg += HANGING_BY_PIECE_MG[p] * self.hanging_bonus_scale_mg
                    eg += HANGING_BY_PIECE_EG[p] * self.hanging_bonus_scale_eg
                elif attackers_bb.bit_count() > defenders:
                    mg += (THREAT_BY_PIECE_MG[p] // 2) * self.attack_pressure_scale_mg
                    eg += (THREAT_BY_PIECE_EG[p] // 2) * self.attack_pressure_scale_eg

                if p in (BQ, WQ):
                    if attackers_bb & own_minors:
                        mg += self.queen_harass_bonus_mg
                        eg += self.queen_harass_bonus_eg
                    elif attackers_bb & own_rooks:
                        mg += self.queen_harass_bonus_mg // 2
                        eg += self.queen_harass_bonus_eg // 2

        return mg, eg

    def _king_safety(
        self,
        board: Board,
        color: int,
        phase: int,
        enemy_attack_map: int,
        own_attack_map: int,
    ) -> tuple[int, int]:
        mg = 0
        eg = 0
        king_sq = board.king_sq(color)
        if king_sq == -1:
            return mg, eg

        enemy = color ^ 1
        kf = file_of(king_sq)
        kr = rank_of(king_sq)
        own_pawns = side_pawns(board, color)
        enemy_pawns = side_pawns(board, enemy)
        enemy_queens = side_queens(board, enemy)
        enemy_has_queen = enemy_queens != 0

        for ff in range(max(0, kf - 1), min(7, kf + 1) + 1):
            nearest = 9
            storm = 9
            if color == WHITE:
                for rr in range(kr + 1, 8):
                    sq = rr * 8 + ff
                    if own_pawns & (1 << sq):
                        nearest = rr - kr
                        break
                for rr in range(kr, -1, -1):
                    sq = rr * 8 + ff
                    if enemy_pawns & (1 << sq):
                        storm = kr - rr + 1
                        break
            else:
                for rr in range(kr - 1, -1, -1):
                    sq = rr * 8 + ff
                    if own_pawns & (1 << sq):
                        nearest = kr - rr
                        break
                for rr in range(kr, 8):
                    sq = rr * 8 + ff
                    if enemy_pawns & (1 << sq):
                        storm = rr - kr + 1
                        break

            if nearest == 1:
                mg += self.king_file_shelter_mg + 6
                eg += self.king_file_shelter_eg
            elif nearest == 2:
                mg += self.king_file_shelter_mg
            elif nearest == 3:
                mg += self.king_file_shelter_mg // 2
            else:
                mg -= self.king_open_file_penalty_mg

            if storm <= 2:
                mg -= self.king_storm_penalty_mg * 2
            elif storm == 3:
                mg -= self.king_storm_penalty_mg

            own_file_pawns = own_pawns & FILE_MASKS[ff]
            enemy_file_pawns = enemy_pawns & FILE_MASKS[ff]
            if own_file_pawns == 0:
                mg -= self.king_half_open_file_penalty_mg
                if enemy_file_pawns == 0:
                    mg -= self.king_open_file_penalty_mg // 2

        if enemy_has_queen and phase >= 14 and file_of(king_sq) in (3, 4) and rank_relative(color, king_sq) <= 1:
            mg -= self.king_center_penalty_mg

        king_zone = KING_ATK[king_sq] | (1 << king_sq)

        attack_units = 0
        attacker_count = 0

        pawn_hits = pawn_attacks_bb(enemy_pawns, enemy) & king_zone
        if pawn_hits:
            attack_units += pawn_hits.bit_count()
            attacker_count += 1

        for sq in iter_bits(side_knights(board, enemy)):
            hits = KNIGHT_ATK[sq] & king_zone
            if hits:
                attack_units += hits.bit_count() * 2
                attacker_count += 1
        for sq in iter_bits(side_bishops(board, enemy)):
            hits = bishop_attacks(sq, board.occ_all) & king_zone
            if hits:
                attack_units += hits.bit_count() * 2
                attacker_count += 1
        for sq in iter_bits(side_rooks(board, enemy)):
            hits = rook_attacks(sq, board.occ_all) & king_zone
            if hits:
                attack_units += hits.bit_count() * 3
                attacker_count += 1
        for sq in iter_bits(side_queens(board, enemy)):
            hits = queen_attacks(sq, board.occ_all) & king_zone
            if hits:
                attack_units += hits.bit_count() * 5
                attacker_count += 1

        attacked_ring = (enemy_attack_map & king_zone).bit_count()
        undefended_ring = ((enemy_attack_map & ~own_attack_map) & king_zone).bit_count()

        mg -= attacked_ring * self.king_attacked_ring_mg
        mg -= undefended_ring * self.king_undefended_ring_mg
        mg -= attack_units * max(0, attacker_count - 1) * self.king_attacker_bonus_mg // 2

        if not enemy_has_queen:
            mg = (mg * 2) // 3

        center_dist = abs(file_of(king_sq) - 3) + abs(rank_of(king_sq) - 3)
        eg += max(0, 7 - center_dist) * 4

        return mg, eg

    def _space(self, board: Board, color: int, enemy_attack_map: int) -> tuple[int, int]:
        mg = 0
        eg = 0

        minors = side_knights(board, color).bit_count() + side_bishops(board, color).bit_count()
        if minors <= 1:
            return mg, eg

        enemy_pawn_attacks = pawn_attacks_bb(side_pawns(board, color ^ 1), color ^ 1)

        zone = 0
        files_mask = FILE_MASKS[2] | FILE_MASKS[3] | FILE_MASKS[4] | FILE_MASKS[5]
        if color == WHITE:
            for r in range(2, 5):
                zone |= RANK_MASKS[r]
        else:
            for r in range(3, 6):
                zone |= RANK_MASKS[r]
        zone &= files_mask
        zone &= ~board.occ[color]

        controlled = 0
        safe_controlled = 0
        for sq in iter_bits(zone):
            if board.attacks_to(sq, color):
                controlled += 1
                if not (enemy_pawn_attacks & (1 << sq)):
                    safe_controlled += 1

        mg += controlled * self.space_bonus_mg
        mg += safe_controlled * self.safe_space_bonus_mg
        return mg, eg

    def _opening_queen_penalty(self, board: Board, color: int) -> tuple[int, int]:
        mg = 0
        eg = 0
        queens = side_queens(board, color)
        if queens == 0:
            return mg, eg

        minors = side_knights(board, color) | side_bishops(board, color)
        undeveloped = 0
        if color == WHITE:
            undeveloped += int(bool(board.bb[WN] & ((1 << 1) | (1 << 6))))
            undeveloped += int(bool(board.bb[WB] & ((1 << 2) | (1 << 5))))
        else:
            undeveloped += int(bool(board.bb[BN] & ((1 << 57) | (1 << 62))))
            undeveloped += int(bool(board.bb[BB] & ((1 << 58) | (1 << 61))))

        for sq in iter_bits(queens):
            if color == WHITE and rank_of(sq) > 1 and undeveloped >= 2:
                mg -= self.queen_early_penalty_mg * undeveloped
            if color == BLACK and rank_of(sq) < 6 and undeveloped >= 2:
                mg -= self.queen_early_penalty_mg * undeveloped

        return mg, eg

    def _mopup(self, board: Board, color: int, phase: int) -> tuple[int, int]:
        if phase > 8:
            return 0, 0

        my_np = self._non_pawn_material(board, color)
        op_np = self._non_pawn_material(board, color ^ 1)
        my_pawns = side_pawns(board, color).bit_count()
        op_pawns = side_pawns(board, color ^ 1).bit_count()

        if my_np + my_pawns * 100 <= op_np + op_pawns * 100 + 150:
            return 0, 0

        own_king = board.king_sq(color)
        enemy_king = board.king_sq(color ^ 1)
        if own_king == -1 or enemy_king == -1:
            return 0, 0

        edge_dist = min(file_of(enemy_king), 7 - file_of(enemy_king)) + min(rank_of(enemy_king), 7 - rank_of(enemy_king))
        king_proximity = 14 - manhattan(own_king, enemy_king)
        bonus = (6 - edge_dist) * 6 + king_proximity * 4
        return bonus // 3, bonus

    def _endgame_scale(self, board: Board, score: int, phase: int) -> int:
        if phase > 6:
            return score

        white_np = self._non_pawn_material(board, WHITE)
        black_np = self._non_pawn_material(board, BLACK)
        white_pawns = board.bb[WP].bit_count()
        black_pawns = board.bb[BP].bit_count()

        if white_pawns == 0 and black_pawns == 0:
            if max(white_np, black_np) <= PIECE_VALUES_MG[WR]:
                score //= 6
            elif max(white_np, black_np) <= PIECE_VALUES_MG[WR] + PIECE_VALUES_MG[WB]:
                score //= 4

        if (
            board.bb[WR] == board.bb[BR] == board.bb[WQ] == board.bb[BQ] == 0 and
            board.bb[WN] == board.bb[BN] == 0 and
            board.bb[WB].bit_count() == 1 and board.bb[BB].bit_count() == 1
        ):
            wbsq, _ = pop_lsb(board.bb[WB])
            bbsq, _ = pop_lsb(board.bb[BB])
            if square_color(wbsq) != square_color(bbsq):
                score = (score * 2) // 3

        if board.bb[WR].bit_count() == 1 and board.bb[BR].bit_count() == 1 and white_np == PIECE_VALUES_MG[WR] and black_np == PIECE_VALUES_MG[WR]:
            if abs(white_pawns - black_pawns) <= 1:
                score = (score * 3) // 4

        return score