from dataclasses import dataclass
from typing import List, Dict, Tuple
import random

U64 = int

WHITE, BLACK = 0, 1

WP, WN, WB, WR, WQ, WK = 0, 1, 2, 3, 4, 5
BP, BN, BB, BR, BQ, BK = 6, 7, 8, 9, 10, 11

RANK_1 = 0xFF
RANK_2 = RANK_1 << 8
RANK_7 = RANK_1 << 48
RANK_8 = RANK_1 << 56

NOT_A = 0xFEFEFEFEFEFEFEFE
NOT_H = 0x7F7F7F7F7F7F7F7F
NOT_AB = 0xFCFCFCFCFCFCFCFC
NOT_GH = 0x3F3F3F3F3F3F3F3F

CASTLE_WK = 1
CASTLE_WQ = 2
CASTLE_BK = 4
CASTLE_BQ = 8

FLAG_NONE = 0
FLAG_CAPTURE = 1
FLAG_EP = 2
FLAG_CASTLE = 4
FLAG_PROMO = 8
FLAG_DBL = 16

PROMO_N, PROMO_B, PROMO_R, PROMO_Q = 1, 2, 3, 4

PIECE_CHARS = "PNBRQKpnbrqk"
CHAR_TO_PIECE = {c: i for i, c in enumerate(PIECE_CHARS)}

SQUARE_NAMES = [f"{chr(97 + (i & 7))}{1 + (i >> 3)}" for i in range(64)]
NAME_TO_SQ = {SQUARE_NAMES[i]: i for i in range(64)}

def bb(sq: int) -> U64:
    return 1 << sq

def lsb(x: U64) -> int:
    return (x & -x).bit_length() - 1

def pop_lsb(x: U64) -> Tuple[int, U64]:
    b = x & -x
    return (b.bit_length() - 1, x ^ b)

def pack_move(fr: int, to: int, promo: int = 0, flags: int = 0) -> int:
    return (fr & 63) | ((to & 63) << 6) | ((promo & 7) << 12) | ((flags & 63) << 15)

def mv_from(m: int) -> int:
    return m & 63

def mv_to(m: int) -> int:
    return (m >> 6) & 63

def mv_promo(m: int) -> int:
    return (m >> 12) & 7

def mv_flags(m: int) -> int:
    return (m >> 15) & 63

KNIGHT_ATK = [0] * 64
KING_ATK = [0] * 64

MASK64 = 0xFFFFFFFFFFFFFFFF

def _init_leapers():
    for sq in range(64):
        b = bb(sq)

        n = 0
        n |= (b << 17) & NOT_A
        n |= (b << 15) & NOT_H
        n |= (b << 10) & NOT_AB
        n |= (b << 6) & NOT_GH
        n |= (b >> 17) & NOT_H
        n |= (b >> 15) & NOT_A
        n |= (b >> 10) & NOT_GH
        n |= (b >> 6) & NOT_AB
        KNIGHT_ATK[sq] = n & MASK64

        k = 0
        k |= (b << 8)
        k |= (b >> 8)
        k |= (b << 1) & NOT_A
        k |= (b >> 1) & NOT_H
        k |= (b << 9) & NOT_A
        k |= (b << 7) & NOT_H
        k |= (b >> 7) & NOT_A
        k |= (b >> 9) & NOT_H
        KING_ATK[sq] = k & MASK64

_init_leapers()

def rook_attacks_onfly(sq: int, occ: U64) -> U64:
    attacks = 0
    s = sq + 8
    while s < 64:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s += 8
    s = sq - 8
    while s >= 0:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s -= 8
    s = sq + 1
    while s < 64 and (s & 7) != 0:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s += 1
    s = sq - 1
    while s >= 0 and (s & 7) != 7:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s -= 1
    return attacks

def bishop_attacks_onfly(sq: int, occ: U64) -> U64:
    attacks = 0
    s = sq + 9
    while s < 64 and (s & 7) != 0:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s += 9
    s = sq + 7
    while s < 64 and (s & 7) != 7:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s += 7
    s = sq - 7
    while s >= 0 and (s & 7) != 0:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s -= 7
    s = sq - 9
    while s >= 0 and (s & 7) != 7:
        attacks |= bb(s)
        if occ & bb(s):
            break
        s -= 9
    return attacks

def _rook_mask(sq: int) -> U64:
    f = sq & 7
    r = sq >> 3
    m = 0
    for rr in range(r + 1, 7):
        m |= bb((rr << 3) | f)
    for rr in range(r - 1, 0, -1):
        m |= bb((rr << 3) | f)
    for ff in range(f + 1, 7):
        m |= bb((r << 3) | ff)
    for ff in range(f - 1, 0, -1):
        m |= bb((r << 3) | ff)
    return m

def _bishop_mask(sq: int) -> U64:
    f = sq & 7
    r = sq >> 3
    m = 0
    rr, ff = r + 1, f + 1
    while rr < 7 and ff < 7:
        m |= bb((rr << 3) | ff)
        rr += 1
        ff += 1
    rr, ff = r + 1, f - 1
    while rr < 7 and ff > 0:
        m |= bb((rr << 3) | ff)
        rr += 1
        ff -= 1
    rr, ff = r - 1, f + 1
    while rr > 0 and ff < 7:
        m |= bb((rr << 3) | ff)
        rr -= 1
        ff += 1
    rr, ff = r - 1, f - 1
    while rr > 0 and ff > 0:
        m |= bb((rr << 3) | ff)
        rr -= 1
        ff -= 1
    return m

def _bits_of(mask: U64) -> List[int]:
    out = []
    m = mask
    while m:
        s, m = pop_lsb(m)
        out.append(s)
    return out

def _set_occupancy(index: int, bits: List[int]) -> U64:
    occ = 0
    for i, sq in enumerate(bits):
        if (index >> i) & 1:
            occ |= bb(sq)
    return occ

def _index_from_occ(occ: U64, bits: List[int]) -> int:
    idx = 0
    for i, sq in enumerate(bits):
        if (occ >> sq) & 1:
            idx |= 1 << i
    return idx

ROOK_MASK = [0] * 64
BISHOP_MASK = [0] * 64
ROOK_BITS: List[List[int]] = [None] * 64
BISHOP_BITS: List[List[int]] = [None] * 64
ROOK_TABLE: List[List[U64]] = [None] * 64
BISHOP_TABLE: List[List[U64]] = [None] * 64

def _init_sliders():
    for sq in range(64):
        rm = _rook_mask(sq)
        bm = _bishop_mask(sq)
        ROOK_MASK[sq] = rm
        BISHOP_MASK[sq] = bm
        rbits = _bits_of(rm)
        bbits = _bits_of(bm)
        ROOK_BITS[sq] = rbits
        BISHOP_BITS[sq] = bbits

        rsize = 1 << len(rbits)
        bsize = 1 << len(bbits)

        rt = [0] * rsize
        bt = [0] * bsize

        for idx in range(rsize):
            occ = _set_occupancy(idx, rbits)
            rt[idx] = rook_attacks_onfly(sq, occ)

        for idx in range(bsize):
            occ = _set_occupancy(idx, bbits)
            bt[idx] = bishop_attacks_onfly(sq, occ)

        ROOK_TABLE[sq] = rt
        BISHOP_TABLE[sq] = bt

_init_sliders()

def rook_attacks(sq: int, occ: U64) -> U64:
    occ &= ROOK_MASK[sq]
    return ROOK_TABLE[sq][_index_from_occ(occ, ROOK_BITS[sq])]

def bishop_attacks(sq: int, occ: U64) -> U64:
    occ &= BISHOP_MASK[sq]
    return BISHOP_TABLE[sq][_index_from_occ(occ, BISHOP_BITS[sq])]

def queen_attacks(sq: int, occ: U64) -> U64:
    return rook_attacks(sq, occ) | bishop_attacks(sq, occ)

_rng = random.Random(0x9E3779B97F4A7C15)
Z_PIECE = [[_rng.getrandbits(64) for _ in range(64)] for _ in range(12)]
Z_SIDE = _rng.getrandbits(64)
Z_CASTLE = [_rng.getrandbits(64) for _ in range(16)]
Z_EP = [_rng.getrandbits(64) for _ in range(64)]

def _can_ep_capture(color: int, ep: int, wp: U64, bp: U64) -> bool:
    if ep == -1:
        return False
    if color == WHITE:
        fr1 = ep - 7
        fr2 = ep - 9
        if 0 <= fr1 < 64 and (bb(fr1) & wp) and ((ep & 7) != 7):
            return True
        if 0 <= fr2 < 64 and (bb(fr2) & wp) and ((ep & 7) != 0):
            return True
        return False
    fr1 = ep + 7
    fr2 = ep + 9
    if 0 <= fr1 < 64 and (bb(fr1) & bp) and ((ep & 7) != 0):
        return True
    if 0 <= fr2 < 64 and (bb(fr2) & bp) and ((ep & 7) != 7):
        return True
    return False

@dataclass
class Undo:
    move: int
    captured: int
    castling: int
    ep: int
    halfmove: int
    fullmove: int
    moved_piece: int
    hash: int

class Board:
    __slots__ = ("bb", "occ", "occ_all", "stm", "castling", "ep", "halfmove", "fullmove",
                 "stack", "piece", "hash", "rep", "history")

    def __init__(self, fen: str = None):
        self.bb = [0] * 12
        self.occ = [0, 0]
        self.occ_all = 0
        self.stm = WHITE
        self.castling = 0
        self.ep = -1
        self.halfmove = 0
        self.fullmove = 1
        self.stack: List[Undo] = []
        self.piece = [-1] * 64
        self.hash = 0
        self.rep: Dict[int, int] = {}
        self.history: List[int] = []
        if fen is None:
            self.set_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        else:
            self.set_fen(fen)

    def _recalc_occ(self):
        w = self.bb[WP] | self.bb[WN] | self.bb[WB] | self.bb[WR] | self.bb[WQ] | self.bb[WK]
        b = self.bb[BP] | self.bb[BN] | self.bb[BB] | self.bb[BR] | self.bb[BQ] | self.bb[BK]
        self.occ[WHITE] = w
        self.occ[BLACK] = b
        self.occ_all = w | b

    def _rebuild_mailbox(self):
        self.piece = [-1] * 64
        for p in range(12):
            m = self.bb[p]
            while m:
                sq, m = pop_lsb(m)
                self.piece[sq] = p

    def _ep_hash(self, color: int, ep: int) -> int:
        if ep == -1:
            return 0
        if _can_ep_capture(color, ep, self.bb[WP], self.bb[BP]):
            return Z_EP[ep]
        return 0

    def compute_hash(self) -> int:
        h = 0
        for p in range(12):
            m = self.bb[p]
            while m:
                sq, m = pop_lsb(m)
                h ^= Z_PIECE[p][sq]
        if self.stm == BLACK:
            h ^= Z_SIDE
        h ^= Z_CASTLE[self.castling]
        h ^= self._ep_hash(self.stm, self.ep)
        return h

    def set_fen(self, fen: str):
        parts = fen.split()
        if len(parts) < 4:
            raise ValueError("Bad FEN")
        for i in range(12):
            self.bb[i] = 0
        rows = parts[0].split("/")
        if len(rows) != 8:
            raise ValueError("Bad FEN board")
        sq = 56
        for row in rows:
            f = 0
            for ch in row:
                if ch.isdigit():
                    f += int(ch)
                else:
                    p = CHAR_TO_PIECE.get(ch)
                    if p is None:
                        raise ValueError("Bad piece")
                    self.bb[p] |= bb(sq + f)
                    f += 1
            if f != 8:
                raise ValueError("Bad rank")
            sq -= 8

        self.stm = WHITE if parts[1] == "w" else BLACK
        c = 0
        if "K" in parts[2]: c |= CASTLE_WK
        if "Q" in parts[2]: c |= CASTLE_WQ
        if "k" in parts[2]: c |= CASTLE_BK
        if "q" in parts[2]: c |= CASTLE_BQ
        self.castling = c
        self.ep = -1 if parts[3] == "-" else NAME_TO_SQ.get(parts[3], -1)
        self.halfmove = int(parts[4]) if len(parts) > 4 else 0
        self.fullmove = int(parts[5]) if len(parts) > 5 else 1
        self.stack.clear()
        self._recalc_occ()
        self._rebuild_mailbox()
        self.hash = self.compute_hash()
        self.history = [self.hash]
        self.rep = {self.hash: 1}

    def fen(self) -> str:
        out = []
        for r in range(7, -1, -1):
            empty = 0
            row = []
            for f in range(8):
                sq = (r << 3) | f
                p = self.piece[sq]
                if p == -1:
                    empty += 1
                else:
                    if empty:
                        row.append(str(empty))
                        empty = 0
                    row.append(PIECE_CHARS[p])
            if empty:
                row.append(str(empty))
            out.append("".join(row))
        side = "w" if self.stm == WHITE else "b"
        c = ""
        c += "K" if self.castling & CASTLE_WK else ""
        c += "Q" if self.castling & CASTLE_WQ else ""
        c += "k" if self.castling & CASTLE_BK else ""
        c += "q" if self.castling & CASTLE_BQ else ""
        if not c:
            c = "-"
        ep = "-" if self.ep == -1 else SQUARE_NAMES[self.ep]
        return f"{'/'.join(out)} {side} {c} {ep} {self.halfmove} {self.fullmove}"

    def __str__(self) -> str:
        rows = []
        for r in range(7, -1, -1):
            row = []
            for f in range(8):
                sq = (r << 3) | f
                p = self.piece[sq]
                row.append("." if p == -1 else PIECE_CHARS[p])
            rows.append(" ".join(row))
        return "\n".join(rows)

    def king_sq(self, color: int) -> int:
        kbb = self.bb[WK if color == WHITE else BK]
        return lsb(kbb) if kbb else -1

    def attacks_to(self, sq: int, by_color: int) -> U64:
        occ = self.occ_all
        sbb = bb(sq)
        att = 0
        if by_color == WHITE:
            pawns = self.bb[WP]
            knights = self.bb[WN]
            bishops = self.bb[WB]
            rooks = self.bb[WR]
            queens = self.bb[WQ]
            king = self.bb[WK]
            pawn_atk = ((sbb >> 7) & NOT_H) | ((sbb >> 9) & NOT_A)
        else:
            pawns = self.bb[BP]
            knights = self.bb[BN]
            bishops = self.bb[BB]
            rooks = self.bb[BR]
            queens = self.bb[BQ]
            king = self.bb[BK]
            pawn_atk = ((sbb << 7) & NOT_A) | ((sbb << 9) & NOT_H)

        att |= pawns & pawn_atk
        att |= knights & KNIGHT_ATK[sq]
        att |= king & KING_ATK[sq]
        bq = bishops | queens
        rq = rooks | queens
        if bq:
            att |= bq & bishop_attacks(sq, occ)
        if rq:
            att |= rq & rook_attacks(sq, occ)
        return att

    def is_attacked(self, sq: int, by_color: int) -> bool:
        return self.attacks_to(sq, by_color) != 0

    def in_check(self, color: int) -> bool:
        ks = self.king_sq(color)
        if ks == -1:
            return False
        return self.is_attacked(ks, color ^ 1)

    def _remove_piece(self, p: int, sq: int):
        self.bb[p] ^= bb(sq)
        self.piece[sq] = -1

    def _add_piece(self, p: int, sq: int):
        self.bb[p] |= bb(sq)
        self.piece[sq] = p

    def _move_piece(self, p: int, fr: int, to: int):
        self.bb[p] ^= bb(fr) | bb(to)
        self.piece[fr] = -1
        self.piece[to] = p

    def _rep_inc(self, h: int):
        self.history.append(h)
        self.rep[h] = self.rep.get(h, 0) + 1

    def _rep_dec(self):
        h = self.history.pop()
        c = self.rep[h] - 1
        if c:
            self.rep[h] = c
        else:
            del self.rep[h]

    def is_threefold(self) -> bool:
        return self.rep.get(self.hash, 0) >= 3

    def is_fifty_move(self) -> bool:
        return self.halfmove >= 100

    def insufficient_material(self) -> bool:
        if self.bb[WP] or self.bb[BP] or self.bb[WR] or self.bb[BR] or self.bb[WQ] or self.bb[BQ]:
            return False
        wn, bn = self.bb[WN], self.bb[BN]
        wb, bb_ = self.bb[WB], self.bb[BB]
        if (wn | bn | wb | bb_) == 0:
            return True
        if (wn != 0) and (wn & (wn - 1) == 0) and (wb | bn | bb_) == 0:
            return True
        if (bn != 0) and (bn & (bn - 1) == 0) and (bb_ | wn | wb) == 0:
            return True
        if (wb != 0) and (wb & (wb - 1) == 0) and (wn | bn | bb_) == 0:
            return True
        if (bb_ != 0) and (bb_ & (bb_ - 1) == 0) and (wn | bn | wb) == 0:
            return True
        if (wb != 0) and (wb & (wb - 1) == 0) and (bb_ != 0) and (bb_ & (bb_ - 1) == 0) and (wn | bn) == 0:
            wsq = lsb(wb)
            bsq = lsb(bb_)
            wcol = ((wsq >> 3) ^ (wsq & 7)) & 1
            bcol = ((bsq >> 3) ^ (bsq & 7)) & 1
            if wcol == bcol:
                return True
        return False

    def make_move(self, m: int) -> bool:
        fr = mv_from(m)
        to = mv_to(m)
        promo = mv_promo(m)
        flags = mv_flags(m)

        moved = self.piece[fr]
        if moved == -1:
            return False
        if (moved < 6) != (self.stm == WHITE):
            return False

        captured = -1
        cap_sq = to
        if flags & FLAG_EP:
            cap_sq = to - 8 if self.stm == WHITE else to + 8
            captured = self.piece[cap_sq]
        else:
            captured = self.piece[to]

        u = Undo(m, captured, self.castling, self.ep, self.halfmove, self.fullmove, moved, self.hash)
        self.stack.append(u)

        h = self.hash
        h ^= self._ep_hash(self.stm, self.ep)
        h ^= Z_CASTLE[self.castling]

        self.ep = -1
        self.halfmove += 1
        if moved in (WP, BP) or (captured != -1):
            self.halfmove = 0

        if captured != -1:
            self._remove_piece(captured, cap_sq)
            h ^= Z_PIECE[captured][cap_sq]

        if flags & FLAG_CASTLE:
            if moved == WK and to == 6:
                self._move_piece(WK, 4, 6)
                self._move_piece(WR, 7, 5)
                h ^= Z_PIECE[WK][4] ^ Z_PIECE[WK][6]
                h ^= Z_PIECE[WR][7] ^ Z_PIECE[WR][5]
            elif moved == WK and to == 2:
                self._move_piece(WK, 4, 2)
                self._move_piece(WR, 0, 3)
                h ^= Z_PIECE[WK][4] ^ Z_PIECE[WK][2]
                h ^= Z_PIECE[WR][0] ^ Z_PIECE[WR][3]
            elif moved == BK and to == 62:
                self._move_piece(BK, 60, 62)
                self._move_piece(BR, 63, 61)
                h ^= Z_PIECE[BK][60] ^ Z_PIECE[BK][62]
                h ^= Z_PIECE[BR][63] ^ Z_PIECE[BR][61]
            elif moved == BK and to == 58:
                self._move_piece(BK, 60, 58)
                self._move_piece(BR, 56, 59)
                h ^= Z_PIECE[BK][60] ^ Z_PIECE[BK][58]
                h ^= Z_PIECE[BR][56] ^ Z_PIECE[BR][59]
            else:
                self.stack.pop()
                return False
        else:
            self._move_piece(moved, fr, to)
            h ^= Z_PIECE[moved][fr] ^ Z_PIECE[moved][to]

        if flags & FLAG_PROMO:
            if self.stm == WHITE:
                self._remove_piece(WP, to)
                h ^= Z_PIECE[WP][to]
                np = {PROMO_N: WN, PROMO_B: WB, PROMO_R: WR, PROMO_Q: WQ}.get(promo, WQ)
                self._add_piece(np, to)
                h ^= Z_PIECE[np][to]
            else:
                self._remove_piece(BP, to)
                h ^= Z_PIECE[BP][to]
                np = {PROMO_N: BN, PROMO_B: BB, PROMO_R: BR, PROMO_Q: BQ}.get(promo, BQ)
                self._add_piece(np, to)
                h ^= Z_PIECE[np][to]

        if moved == WK:
            self.castling &= ~(CASTLE_WK | CASTLE_WQ)
        elif moved == BK:
            self.castling &= ~(CASTLE_BK | CASTLE_BQ)
        elif moved == WR:
            if fr == 0: self.castling &= ~CASTLE_WQ
            elif fr == 7: self.castling &= ~CASTLE_WK
        elif moved == BR:
            if fr == 56: self.castling &= ~CASTLE_BQ
            elif fr == 63: self.castling &= ~CASTLE_BK

        if captured == WR:
            if to == 0: self.castling &= ~CASTLE_WQ
            elif to == 7: self.castling &= ~CASTLE_WK
        elif captured == BR:
            if to == 56: self.castling &= ~CASTLE_BQ
            elif to == 63: self.castling &= ~CASTLE_BK

        if flags & FLAG_DBL:
            self.ep = fr + 8 if self.stm == WHITE else fr - 8

        if self.stm == BLACK:
            self.fullmove += 1

        self.stm ^= 1
        h ^= Z_SIDE
        h ^= Z_CASTLE[self.castling]
        h ^= self._ep_hash(self.stm, self.ep)
        self.hash = h

        self._recalc_occ()
        self._rep_inc(self.hash)

        if self.in_check(self.stm ^ 1):
            self.unmake_move()
            return False
        return True

    def unmake_move(self):
        self._rep_dec()
        u = self.stack.pop()

        m = u.move
        fr = mv_from(m)
        to = mv_to(m)
        promo = mv_promo(m)
        flags = mv_flags(m)
        moved = u.moved_piece
        captured = u.captured

        self.stm ^= 1
        self.castling = u.castling
        self.ep = u.ep
        self.halfmove = u.halfmove
        self.fullmove = u.fullmove
        self.hash = u.hash

        if flags & FLAG_CASTLE:
            if moved == WK and to == 6:
                self._move_piece(WK, 6, 4)
                self._move_piece(WR, 5, 7)
            elif moved == WK and to == 2:
                self._move_piece(WK, 2, 4)
                self._move_piece(WR, 3, 0)
            elif moved == BK and to == 62:
                self._move_piece(BK, 62, 60)
                self._move_piece(BR, 61, 63)
            elif moved == BK and to == 58:
                self._move_piece(BK, 58, 60)
                self._move_piece(BR, 59, 56)
        else:
            if flags & FLAG_PROMO:
                if self.stm == WHITE:
                    np = {PROMO_N: WN, PROMO_B: WB, PROMO_R: WR, PROMO_Q: WQ}.get(promo, WQ)
                    self._remove_piece(np, to)
                    self._add_piece(WP, to)
                else:
                    np = {PROMO_N: BN, PROMO_B: BB, PROMO_R: BR, PROMO_Q: BQ}.get(promo, BQ)
                    self._remove_piece(np, to)
                    self._add_piece(BP, to)
            self._move_piece(moved, to, fr)

        if captured != -1:
            if flags & FLAG_EP:
                cap_sq = to - 8 if self.stm == WHITE else to + 8
                self._add_piece(captured, cap_sq)
            else:
                self._add_piece(captured, to)

        self._recalc_occ()

    def _gen_pawn_moves(self, moves: List[int], color: int):
        occ = self.occ_all
        them = self.occ[color ^ 1]
        pawns = self.bb[WP if color == WHITE else BP]

        if color == WHITE:
            one = (pawns << 8) & ~occ
            promo = one & RANK_8
            quiet = one & ~RANK_8
            while promo:
                to, promo = pop_lsb(promo)
                fr = to - 8
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_PROMO))
            while quiet:
                to, quiet = pop_lsb(quiet)
                moves.append(pack_move(to - 8, to, 0, FLAG_NONE))
            two = ((pawns & RANK_2) << 16) & ~occ & ~(occ << 8)
            while two:
                to, two = pop_lsb(two)
                moves.append(pack_move(to - 16, to, 0, FLAG_DBL))
            capL = ((pawns << 7) & NOT_H) & them
            capR = ((pawns << 9) & NOT_A) & them
            promoL = capL & RANK_8
            promoR = capR & RANK_8
            capLq = capL & ~RANK_8
            capRq = capR & ~RANK_8
            while promoL:
                to, promoL = pop_lsb(promoL)
                fr = to - 7
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_CAPTURE | FLAG_PROMO))
            while promoR:
                to, promoR = pop_lsb(promoR)
                fr = to - 9
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_CAPTURE | FLAG_PROMO))
            while capLq:
                to, capLq = pop_lsb(capLq)
                moves.append(pack_move(to - 7, to, 0, FLAG_CAPTURE))
            while capRq:
                to, capRq = pop_lsb(capRq)
                moves.append(pack_move(to - 9, to, 0, FLAG_CAPTURE))
            if self.ep != -1:
                ep = self.ep
                epb = bb(ep)
                epL = ((pawns << 7) & NOT_H) & epb
                epR = ((pawns << 9) & NOT_A) & epb
                if epL:
                    moves.append(pack_move(ep - 7, ep, 0, FLAG_EP | FLAG_CAPTURE))
                if epR:
                    moves.append(pack_move(ep - 9, ep, 0, FLAG_EP | FLAG_CAPTURE))
        else:
            one = (pawns >> 8) & ~occ
            promo = one & RANK_1
            quiet = one & ~RANK_1
            while promo:
                to, promo = pop_lsb(promo)
                fr = to + 8
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_PROMO))
            while quiet:
                to, quiet = pop_lsb(quiet)
                moves.append(pack_move(to + 8, to, 0, FLAG_NONE))
            two = ((pawns & RANK_7) >> 16) & ~occ & ~(occ >> 8)
            while two:
                to, two = pop_lsb(two)
                moves.append(pack_move(to + 16, to, 0, FLAG_DBL))
            capL = ((pawns >> 9) & NOT_H) & them
            capR = ((pawns >> 7) & NOT_A) & them
            promoL = capL & RANK_1
            promoR = capR & RANK_1
            capLq = capL & ~RANK_1
            capRq = capR & ~RANK_1
            while promoL:
                to, promoL = pop_lsb(promoL)
                fr = to + 9
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_CAPTURE | FLAG_PROMO))
            while promoR:
                to, promoR = pop_lsb(promoR)
                fr = to + 7
                for pr in (PROMO_N, PROMO_B, PROMO_R, PROMO_Q):
                    moves.append(pack_move(fr, to, pr, FLAG_CAPTURE | FLAG_PROMO))
            while capLq:
                to, capLq = pop_lsb(capLq)
                moves.append(pack_move(to + 9, to, 0, FLAG_CAPTURE))
            while capRq:
                to, capRq = pop_lsb(capRq)
                moves.append(pack_move(to + 7, to, 0, FLAG_CAPTURE))
            if self.ep != -1:
                ep = self.ep
                epb = bb(ep)
                epL = ((pawns >> 9) & NOT_H) & epb
                epR = ((pawns >> 7) & NOT_A) & epb
                if epL:
                    moves.append(pack_move(ep + 9, ep, 0, FLAG_EP | FLAG_CAPTURE))
                if epR:
                    moves.append(pack_move(ep + 7, ep, 0, FLAG_EP | FLAG_CAPTURE))

    def _gen_piece_moves_leaper(self, moves: List[int], p: int, atk: List[U64], color: int):
        us = self.occ[color]
        them = self.occ[color ^ 1]
        pieces = self.bb[p]
        while pieces:
            fr, pieces = pop_lsb(pieces)
            at = atk[fr] & ~us
            caps = at & them
            quiet = at & ~them
            while caps:
                to, caps = pop_lsb(caps)
                moves.append(pack_move(fr, to, 0, FLAG_CAPTURE))
            while quiet:
                to, quiet = pop_lsb(quiet)
                moves.append(pack_move(fr, to, 0, FLAG_NONE))

    def _gen_piece_moves_slider(self, moves: List[int], p: int, color: int, kind: int):
        us = self.occ[color]
        them = self.occ[color ^ 1]
        occ = self.occ_all
        pieces = self.bb[p]
        while pieces:
            fr, pieces = pop_lsb(pieces)
            if kind == 0:
                at = bishop_attacks(fr, occ)
            elif kind == 1:
                at = rook_attacks(fr, occ)
            else:
                at = queen_attacks(fr, occ)
            at &= ~us
            caps = at & them
            quiet = at & ~them
            while caps:
                to, caps = pop_lsb(caps)
                moves.append(pack_move(fr, to, 0, FLAG_CAPTURE))
            while quiet:
                to, quiet = pop_lsb(quiet)
                moves.append(pack_move(fr, to, 0, FLAG_NONE))

    def _gen_king_castles(self, moves: List[int], color: int):
        if color == WHITE:
            if (self.castling & CASTLE_WK) and not (self.occ_all & (bb(5) | bb(6))):
                if not self.is_attacked(4, BLACK) and not self.is_attacked(5, BLACK) and not self.is_attacked(6, BLACK):
                    moves.append(pack_move(4, 6, 0, FLAG_CASTLE))
            if (self.castling & CASTLE_WQ) and not (self.occ_all & (bb(1) | bb(2) | bb(3))):
                if not self.is_attacked(4, BLACK) and not self.is_attacked(3, BLACK) and not self.is_attacked(2, BLACK):
                    moves.append(pack_move(4, 2, 0, FLAG_CASTLE))
        else:
            if (self.castling & CASTLE_BK) and not (self.occ_all & (bb(61) | bb(62))):
                if not self.is_attacked(60, WHITE) and not self.is_attacked(61, WHITE) and not self.is_attacked(62, WHITE):
                    moves.append(pack_move(60, 62, 0, FLAG_CASTLE))
            if (self.castling & CASTLE_BQ) and not (self.occ_all & (bb(57) | bb(58) | bb(59))):
                if not self.is_attacked(60, WHITE) and not self.is_attacked(59, WHITE) and not self.is_attacked(58, WHITE):
                    moves.append(pack_move(60, 58, 0, FLAG_CASTLE))

    def generate_pseudo_legal(self) -> List[int]:
        color = self.stm
        moves: List[int] = []
        self._gen_pawn_moves(moves, color)
        if color == WHITE:
            self._gen_piece_moves_leaper(moves, WN, KNIGHT_ATK, color)
            self._gen_piece_moves_slider(moves, WB, color, 0)
            self._gen_piece_moves_slider(moves, WR, color, 1)
            self._gen_piece_moves_slider(moves, WQ, color, 2)
            self._gen_piece_moves_leaper(moves, WK, KING_ATK, color)
        else:
            self._gen_piece_moves_leaper(moves, BN, KNIGHT_ATK, color)
            self._gen_piece_moves_slider(moves, BB, color, 0)
            self._gen_piece_moves_slider(moves, BR, color, 1)
            self._gen_piece_moves_slider(moves, BQ, color, 2)
            self._gen_piece_moves_leaper(moves, BK, KING_ATK, color)
        self._gen_king_castles(moves, color)
        return moves

    def generate_legal(self) -> List[int]:
        pse = self.generate_pseudo_legal()
        out: List[int] = []
        for m in pse:
            if self.make_move(m):
                out.append(m)
                self.unmake_move()
        return out

    def move_to_uci(self, m: int) -> str:
        fr = mv_from(m)
        to = mv_to(m)
        promo = mv_promo(m)
        s = SQUARE_NAMES[fr] + SQUARE_NAMES[to]
        if mv_flags(m) & FLAG_PROMO:
            s += {PROMO_N: "n", PROMO_B: "b", PROMO_R: "r", PROMO_Q: "q"}.get(promo, "q")
        return s

    def uci_to_move(self, u: str) -> int:
        if len(u) < 4:
            return -1
        fr = NAME_TO_SQ.get(u[0:2], -1)
        to = NAME_TO_SQ.get(u[2:4], -1)
        if fr == -1 or to == -1:
            return -1
        promo = 0
        if len(u) >= 5:
            promo = {"n": PROMO_N, "b": PROMO_B, "r": PROMO_R, "q": PROMO_Q}.get(u[4].lower(), 0)
        for m in self.generate_legal():
            if mv_from(m) == fr and mv_to(m) == to:
                if (mv_flags(m) & FLAG_PROMO) == 0 and promo == 0:
                    return m
                if (mv_flags(m) & FLAG_PROMO) and mv_promo(m) == promo:
                    return m
        return -1

    def has_legal_moves(self) -> bool:
        for m in self.generate_pseudo_legal():
            if self.make_move(m):
                self.unmake_move()
                return True
        return False

    def is_checkmate(self) -> bool:
        return self.in_check(self.stm) and not self.has_legal_moves()

    def is_stalemate(self) -> bool:
        return (not self.in_check(self.stm)) and (not self.has_legal_moves())

    def draw_state(self) -> str:
        if self.is_fifty_move():
            return "50-move"
        if self.is_threefold():
            return "threefold"
        if self.insufficient_material():
            return "insufficient"
        if self.is_stalemate():
            return "stalemate"
        return ""

def perft(b: Board, depth: int) -> int:
    if depth <= 0:
        return 1
    n = 0
    for m in b.generate_pseudo_legal():
        if b.make_move(m):
            n += perft(b, depth - 1)
            b.unmake_move()
    return n

if __name__ == "__main__":
    b = Board()
    print(b)
    print(b.fen())
    print("legal:", len(b.generate_legal()))
    for i in range(4):
        print("perft"+str(i+2)+":", perft(b, i+2))
