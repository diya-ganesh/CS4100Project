import math
from dataclasses import dataclass
from archive.board_representations.board_rep import Board, WHITE, BLACK, WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK

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

ROOK_PST = [
      0,   0,   0,   5,   5,   0,   0,   0,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
     -5,   0,   0,   0,   0,   0,   0,  -5,
      5,  10,  10,  10,  10,  10,  10,   5,
      0,   0,   0,   0,   0,   0,   0,   0,
]

QUEEN_PST = [
    -20, -10, -10,  -5,  -5, -10, -10, -20,
    -10,   0,   0,   0,   0,   5,   0, -10,
    -10,   0,   5,   5,   5,   5,   5, -10,
     -5,   0,   5,   5,   5,   5,   0,  -5,
      0,   0,   5,   5,   5,   5,   0,  -5,
    -10,   5,   5,   5,   5,   5,   0, -10,
    -10,   0,   5,   0,   0,   0,   0, -10,
    -20, -10, -10,  -5,  -5, -10, -10, -20,
]

KING_MID_PST = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
     20,  20,   0,   0,   0,   0,  20,  20,
     20,  30,  10,   0,   0,  10,  30,  20,
]

KING_END_PST = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,   0,   0, -10, -20, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  30,  40,  40,  30, -10, -30,
    -30, -10,  20,  30,  30,  20, -10, -30,
    -30, -30,   0,   0,   0,   0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50,
]

PST = {
    WP: PAWN_PST,
    WN: KNIGHT_PST,
    WB: BISHOP_PST,
    WR: ROOK_PST,
    WQ: QUEEN_PST,
    BP: PAWN_PST,
    BN: KNIGHT_PST,
    BB: BISHOP_PST,
    BR: ROOK_PST,
    BQ: QUEEN_PST,
}

def lsb(x):
    return (x & -x).bit_length() - 1

def pop_lsb(x):
    b = x & -x
    return b.bit_length() - 1, x ^ b

def mirror_sq(sq):
    return sq ^ 56

def game_phase(board):
    phase = 0
    phase += (board.bb[WN].bit_count() + board.bb[BN].bit_count()) * 1
    phase += (board.bb[WB].bit_count() + board.bb[BB].bit_count()) * 1
    phase += (board.bb[WR].bit_count() + board.bb[BR].bit_count()) * 2
    phase += (board.bb[WQ].bit_count() + board.bb[BQ].bit_count()) * 4
    return min(phase, 24)

def terminal_score(board, ply):
    legal = board.generate_legal()
    if legal:
        return None
    side = board.stm
    if board.in_check(side):
        return -100000 + ply if side == WHITE else 100000 - ply
    return 0

def material_and_pst(board):
    score = 0
    phase = game_phase(board)
    for p in range(12):
        bbp = board.bb[p]
        while bbp:
            sq, bbp = pop_lsb(bbp)
            val = PIECE_VALUES[p]
            if p < 6:
                score += val
                if p == WK:
                    mid = KING_MID_PST[sq]
                    end = KING_END_PST[sq]
                    score += (mid * phase + end * (24 - phase)) // 24
                else:
                    score += PST[p][sq]
            else:
                score -= val
                msq = mirror_sq(sq)
                if p == BK:
                    mid = KING_MID_PST[msq]
                    end = KING_END_PST[msq]
                    score -= (mid * phase + end * (24 - phase)) // 24
                else:
                    score -= PST[p][msq]
    return score

def mobility(board):
    own = len(board.generate_legal())
    board.stm ^= 1
    opp = len(board.generate_legal())
    board.stm ^= 1
    return 4 * (own - opp) if board.stm == WHITE else 4 * (opp - own)

def center_control(board):
    centers = (1 << 27) | (1 << 28) | (1 << 35) | (1 << 36)
    score = 0
    for sq in (27, 28, 35, 36):
        if board.attacks_to(sq, WHITE):
            score += 8
        if board.attacks_to(sq, BLACK):
            score -= 8
    wp = board.occ[WHITE] & centers
    bp = board.occ[BLACK] & centers
    score += 12 * wp.bit_count()
    score -= 12 * bp.bit_count()
    return score

def pawn_structure(board):
    score = 0
    wp = board.bb[WP]
    bp = board.bb[BP]
    for file_idx in range(8):
        file_mask = 0x0101010101010101 << file_idx
        wc = (wp & file_mask).bit_count()
        bc = (bp & file_mask).bit_count()
        if wc > 1:
            score -= 12 * (wc - 1)
        if bc > 1:
            score += 12 * (bc - 1)
    isolated_penalty = 14
    for file_idx in range(8):
        file_mask = 0x0101010101010101 << file_idx
        adj = 0
        if file_idx > 0:
            adj |= 0x0101010101010101 << (file_idx - 1)
        if file_idx < 7:
            adj |= 0x0101010101010101 << (file_idx + 1)
        pawns = wp & file_mask
        if pawns and not (wp & adj):
            score -= isolated_penalty * pawns.bit_count()
        pawns = bp & file_mask
        if pawns and not (bp & adj):
            score += isolated_penalty * pawns.bit_count()
    return score

def evaluate(board):
    term = terminal_score(board, 0)
    if term is not None:
        return term
    if hasattr(board, "is_draw") and board.is_draw():
        return 0
    score = 0
    score += material_and_pst(board)
    score += mobility(board)
    score += center_control(board)
    score += pawn_structure(board)
    return score

@dataclass(slots=True)
class BeamNode:
    path: tuple
    score: int

class LocalBeamSearch:
    __slots__ = ("beam_width", "depth", "expand_width", "temperature", "side")

    def __init__(self, beam_width=16, depth=4, expand_width=24, temperature=1.0):
        self.beam_width = beam_width
        self.depth = depth
        self.expand_width = expand_width
        self.temperature = temperature
        self.side = WHITE

    def _move_score(self, board, move):
        board.make_move(move)
        s = evaluate(board)
        board.unmake_move()
        return s

    def _ordered_moves(self, board):
        moves = board.generate_legal()
        scored = [(self._move_score(board, m), m) for m in moves]
        reverse = board.stm == WHITE
        scored.sort(key=lambda x: x[0], reverse=reverse)
        return [m for _, m in scored]

    def _apply_path(self, board, path):
        for m in path:
            if not board.make_move(m):
                return False
        return True

    def _rollback_path(self, board, path_len):
        for _ in range(path_len):
            board.unmake_move()

    def search(self, board):
        legal = board.generate_legal()
        if not legal:
            return None
        self.side = board.stm
        ordered = self._ordered_moves(board)
        beam = [BeamNode((m,), self._move_score(board, m)) for m in ordered[:self.beam_width]]
        best = max(beam, key=lambda n: n.score) if self.side == WHITE else min(beam, key=lambda n: n.score)
        for depth_idx in range(2, self.depth + 1):
            candidates = []
            for node in beam:
                if not self._apply_path(board, node.path):
                    self._rollback_path(board, len(node.path))
                    continue
                next_moves = self._ordered_moves(board)[:self.expand_width]
                if not next_moves:
                    s = evaluate(board)
                    candidates.append(BeamNode(node.path, s))
                    self._rollback_path(board, len(node.path))
                    continue
                for m in next_moves:
                    board.make_move(m)
                    s = evaluate(board)
                    board.unmake_move()
                    candidates.append(BeamNode(node.path + (m,), s))
                self._rollback_path(board, len(node.path))
            if not candidates:
                break
            reverse = self.side == WHITE
            candidates.sort(key=lambda n: n.score, reverse=reverse)
            beam = candidates[:self.beam_width]
            current = beam[0]
            if (self.side == WHITE and current.score > best.score) or (self.side == BLACK and current.score < best.score):
                best = current
        return best.path[0]

    def search_uci(self, board):
        move = self.search(board)
        return None if move is None else board.move_to_uci(move)

if __name__ == "__main__":
    b = Board()
    s = LocalBeamSearch(beam_width=20, depth=4, expand_width=24)
    m = s.search(b)
    print(b.move_to_uci(m) if m is not None else None)