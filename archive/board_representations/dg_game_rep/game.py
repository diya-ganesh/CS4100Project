import pygame
import sys
import chess

TILE = 90
BOARD_SIZE = TILE * 8
WHITE_TILE = (245, 235, 215)
DARK_TILE = (75, 115, 70)
HIGHLIGHT = (186, 202, 68, 150)
VALID_DOT = (90, 60, 35, 200)
CHECK_COLOR = (235, 67, 52, 160)
PIECE_RADIUS = TILE // 3
WHITE_PIECE = (245, 230, 200)
BLACK_PIECE = (90, 60, 35)

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE + 36))
pygame.display.set_caption("Chess")
piece_font = pygame.font.SysFont("Consolas", 32, bold=True)
status_font = pygame.font.SysFont("Consolas", 16)

board = chess.Board()
selected_sq = None
valid_moves = []

def make_board():
    for row in range(8):
        for col in range(8):
            color = WHITE_TILE if (row + col) % 2 == 0 else DARK_TILE
            pygame.draw.rect(screen, color, (col * TILE, row * TILE, TILE, TILE))


def make_piece(sq, piece, cx=None, cy=None):
    if cx is None:
        px, py = sq_to_pos(sq)
        cx, cy = px + TILE // 2, py + TILE // 2
    is_w = piece.color == chess.WHITE
    pygame.draw.circle(screen, WHITE_PIECE if is_w else BLACK_PIECE, (cx, cy), PIECE_RADIUS)
    pygame.draw.circle(screen, (80, 80, 80) if is_w else (170, 140, 110), (cx, cy), PIECE_RADIUS, 2)
    label = 'N' if piece.piece_type == chess.KNIGHT else chess.piece_name(piece.piece_type)[0].upper()
    txt = piece_font.render(label, True, (30, 30, 30) if is_w else (230, 215, 190))
    screen.blit(txt, txt.get_rect(center=(cx, cy)))


def make_pieces():
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if p:
            make_piece(sq, p)


def make_highlights():
    if board.is_check():
        ksq = board.king(board.turn)
        if ksq is not None:
            kx, ky = sq_to_pos(ksq)
            s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            s.fill(CHECK_COLOR)
            screen.blit(s, (kx, ky))

    if selected_sq is not None:
        sx, sy = sq_to_pos(selected_sq)
        s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        s.fill(HIGHLIGHT)
        screen.blit(s, (sx, sy))

        for dest in valid_moves:
            dx, dy = sq_to_pos(dest)
            ds = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            if board.piece_at(dest):
                pygame.draw.circle(ds, VALID_DOT, (TILE // 2, TILE // 2), TILE // 2, 6)
            else:
                pygame.draw.circle(ds, VALID_DOT, (TILE // 2, TILE // 2), 12)
            screen.blit(ds, (dx, dy))



def sq_to_pos(sq):
    col = chess.square_file(sq)
    row = 7 - chess.square_rank(sq)
    return col * TILE, row * TILE


def pos_to_sq(pos):
    col, row = pos[0] // TILE, pos[1] // TILE
    if 0 <= col < 8 and 0 <= row < 8:
        return chess.square(col, 7 - row)
    return None


def get_destinations(sq):
    return list({m.to_square for m in board.legal_moves if m.from_square == sq})


def promotion(fr, to):
    return any(m.promotion for m in board.legal_moves if m.from_square == fr and m.to_square == to)


def make_promotion(to_sq):
    tx, ty = sq_to_pos(to_sq)
    d = 1 if ty == 0 else -1
    for i, pt in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
        bx, by = tx, ty + i * TILE * d
        if 0 <= by < BOARD_SIZE:
            pygame.draw.rect(screen, (255, 255, 240), (bx, by, TILE, TILE))
            pygame.draw.rect(screen, (60, 60, 60), (bx, by, TILE, TILE), 2)
            make_piece(None, chess.Piece(pt, board.turn), bx + TILE // 2, by + TILE // 2)



def show_status():
    pygame.draw.rect(screen, (40, 40, 40), (0, BOARD_SIZE, BOARD_SIZE, 36))
    turn = "White" if board.turn else "Black"
    if board.is_checkmate():
        msg = f"Checkmate! {'Black' if board.turn else 'White'} wins"
    elif (board.is_stalemate() or board.is_insufficient_material() 
          or board.is_seventyfive_moves()):
        msg = "Stalemate!"
    elif board.is_check():
        msg = f"Check! {turn} to move"
    else:
        msg = f"{turn} to move"
    screen.blit(status_font.render(msg, True, (220, 220, 220)), (10, BOARD_SIZE + 8))
    hint = status_font.render("U: Undo  N: New", True, (130, 130, 130))
    screen.blit(hint, (BOARD_SIZE - hint.get_width() - 10, BOARD_SIZE + 8))

promoting = False
promo_from = None
promo_to = None
fen = []

clock = pygame.time.Clock()
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            if promoting:
                tx, ty = sq_to_pos(promo_to)
                d = 1 if ty == 0 else -1
                for i, pt in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
                    r = pygame.Rect(tx, ty + i * TILE * d, TILE, TILE)
                    if r.collidepoint(e.pos):
                        board.push(chess.Move(promo_from, promo_to, promotion=pt))
                        break
                promoting = False
                selected_sq = None
                valid_moves = []
                continue

            sq = pos_to_sq(e.pos)
            if sq is None:
                continue

            if selected_sq is None:
                p = board.piece_at(sq)
                if p and p.color == board.turn:
                    selected_sq = sq
                    valid_moves = get_destinations(sq)
            else:
                if sq in valid_moves:
                    if promotion(selected_sq, sq):
                        promoting = True
                        promo_from, promo_to = selected_sq, sq
                    else:
                        board.push(chess.Move(selected_sq, sq))
                    selected_sq = None
                    valid_moves = []
                else:
                    selected_sq = None
                    valid_moves = []
                    p = board.piece_at(sq)
                    if p and p.color == board.turn:
                        selected_sq = sq
                        valid_moves = get_destinations(sq)

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_u and board.move_stack:
                board.pop()
                selected_sq = None
                valid_moves = []
                promoting = False
            elif e.key == pygame.K_n:
                board.reset()
                selected_sq = None
                valid_moves = []
                promoting = False

    make_board()
    make_highlights()
    make_pieces()
    if promoting:
        make_promotion(promo_to)
    show_status()
    pygame.display.flip()
    clock.tick(60)