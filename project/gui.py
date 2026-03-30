from __future__ import annotations

import sys
from dataclasses import dataclass

import chess
import pygame

from app import Bot, default_bots
from board import Board

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


@dataclass(slots=True)
class GuiConfig:
    bot: Bot | None = None
    bot_plays_black: bool = True


def run_gui(config: GuiConfig) -> None:
    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE + 36))
    pygame.display.set_caption("Chess Bot GUI")
    piece_font = pygame.font.SysFont("Consolas", 32, bold=True)
    status_font = pygame.font.SysFont("Consolas", 16)

    py_board = chess.Board()
    engine_board = Board()
    selected_sq = None
    valid_moves: list[int] = []
    promoting = False
    promo_from = None
    promo_to = None
    clock = pygame.time.Clock()

    def sync_engine() -> None:
        nonlocal engine_board
        engine_board = Board(py_board.fen())

    def make_board() -> None:
        for row in range(8):
            for col in range(8):
                color = WHITE_TILE if (row + col) % 2 == 0 else DARK_TILE
                pygame.draw.rect(screen, color, (col * TILE, row * TILE, TILE, TILE))

    def sq_to_pos(sq: int) -> tuple[int, int]:
        col = chess.square_file(sq)
        row = 7 - chess.square_rank(sq)
        return col * TILE, row * TILE

    def pos_to_sq(pos: tuple[int, int]) -> int | None:
        col, row = pos[0] // TILE, pos[1] // TILE
        if 0 <= col < 8 and 0 <= row < 8:
            return chess.square(col, 7 - row)
        return None

    def make_piece(sq: int | None, piece: chess.Piece, cx: int | None = None, cy: int | None = None) -> None:
        if cx is None or cy is None:
            assert sq is not None
            px, py = sq_to_pos(sq)
            cx, cy = px + TILE // 2, py + TILE // 2
        is_w = piece.color == chess.WHITE
        pygame.draw.circle(screen, WHITE_PIECE if is_w else BLACK_PIECE, (cx, cy), PIECE_RADIUS)
        pygame.draw.circle(screen, (80, 80, 80) if is_w else (170, 140, 110), (cx, cy), PIECE_RADIUS, 2)
        label = "N" if piece.piece_type == chess.KNIGHT else chess.piece_name(piece.piece_type)[0].upper()
        txt = piece_font.render(label, True, (30, 30, 30) if is_w else (230, 215, 190))
        screen.blit(txt, txt.get_rect(center=(cx, cy)))

    def make_pieces() -> None:
        for sq in chess.SQUARES:
            piece = py_board.piece_at(sq)
            if piece:
                make_piece(sq, piece)

    def make_highlights() -> None:
        if py_board.is_check():
            ksq = py_board.king(py_board.turn)
            if ksq is not None:
                kx, ky = sq_to_pos(ksq)
                surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                surf.fill(CHECK_COLOR)
                screen.blit(surf, (kx, ky))

        if selected_sq is not None:
            sx, sy = sq_to_pos(selected_sq)
            surf = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
            surf.fill(HIGHLIGHT)
            screen.blit(surf, (sx, sy))
            for dest in valid_moves:
                dx, dy = sq_to_pos(dest)
                ds = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                if py_board.piece_at(dest):
                    pygame.draw.circle(ds, VALID_DOT, (TILE // 2, TILE // 2), TILE // 2, 6)
                else:
                    pygame.draw.circle(ds, VALID_DOT, (TILE // 2, TILE // 2), 12)
                screen.blit(ds, (dx, dy))

    def get_destinations(sq: int) -> list[int]:
        return list({m.to_square for m in py_board.legal_moves if m.from_square == sq})

    def needs_promotion(fr: int, to: int) -> bool:
        return any(m.promotion for m in py_board.legal_moves if m.from_square == fr and m.to_square == to)

    def make_promotion(to_sq: int) -> None:
        tx, ty = sq_to_pos(to_sq)
        direction = 1 if ty == 0 else -1
        for i, pt in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
            bx, by = tx, ty + i * TILE * direction
            if 0 <= by < BOARD_SIZE:
                pygame.draw.rect(screen, (255, 255, 240), (bx, by, TILE, TILE))
                pygame.draw.rect(screen, (60, 60, 60), (bx, by, TILE, TILE), 2)
                make_piece(None, chess.Piece(pt, py_board.turn), bx + TILE // 2, by + TILE // 2)

    def show_status() -> None:
        pygame.draw.rect(screen, (40, 40, 40), (0, BOARD_SIZE, BOARD_SIZE, 36))
        turn = "White" if py_board.turn else "Black"
        if py_board.is_checkmate():
            msg = f"Checkmate! {'Black' if py_board.turn else 'White'} wins"
        elif py_board.is_stalemate() or py_board.is_insufficient_material() or py_board.is_seventyfive_moves():
            msg = "Draw"
        elif py_board.is_check():
            msg = f"Check! {turn} to move"
        else:
            msg = f"{turn} to move"
        screen.blit(status_font.render(msg, True, (220, 220, 220)), (10, BOARD_SIZE + 8))
        hint = status_font.render("U: Undo  N: New  B: Bot move", True, (130, 130, 130))
        screen.blit(hint, (BOARD_SIZE - hint.get_width() - 10, BOARD_SIZE + 8))

    def maybe_bot_move() -> None:
        if config.bot is None or py_board.is_game_over():
            return
        bot_turn = (py_board.turn == chess.BLACK and config.bot_plays_black) or (
            py_board.turn == chess.WHITE and not config.bot_plays_black
        )
        if not bot_turn:
            return
        sync_engine()
        result = config.bot.choose_move(engine_board)
        if result.move is not None:
            py_board.push(chess.Move.from_uci(engine_board.move_to_uci(result.move)))

    while True:
        maybe_bot_move()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bot_turn = config.bot is not None and (
                    (py_board.turn == chess.BLACK and config.bot_plays_black)
                    or (py_board.turn == chess.WHITE and not config.bot_plays_black)
                )
                if bot_turn:
                    continue

                if promoting:
                    tx, ty = sq_to_pos(promo_to)
                    direction = 1 if ty == 0 else -1
                    for i, pt in enumerate([chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]):
                        rect = pygame.Rect(tx, ty + i * TILE * direction, TILE, TILE)
                        if rect.collidepoint(event.pos):
                            py_board.push(chess.Move(promo_from, promo_to, promotion=pt))
                            sync_engine()
                            break
                    promoting = False
                    selected_sq = None
                    valid_moves = []
                    continue

                sq = pos_to_sq(event.pos)
                if sq is None:
                    continue

                if selected_sq is None:
                    piece = py_board.piece_at(sq)
                    if piece and piece.color == py_board.turn:
                        selected_sq = sq
                        valid_moves = get_destinations(sq)
                else:
                    if sq in valid_moves:
                        if needs_promotion(selected_sq, sq):
                            promoting = True
                            promo_from, promo_to = selected_sq, sq
                        else:
                            py_board.push(chess.Move(selected_sq, sq))
                            sync_engine()
                        selected_sq = None
                        valid_moves = []
                    else:
                        selected_sq = None
                        valid_moves = []

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u and py_board.move_stack:
                    py_board.pop()
                    sync_engine()
                    selected_sq = None
                    valid_moves = []
                    promoting = False
                elif event.key == pygame.K_n:
                    py_board.reset()
                    sync_engine()
                    selected_sq = None
                    valid_moves = []
                    promoting = False
                elif event.key == pygame.K_b:
                    maybe_bot_move()

        make_board()
        make_highlights()
        make_pieces()
        if promoting:
            make_promotion(promo_to)
        show_status()
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_gui(GuiConfig(bot=default_bots()[0], bot_plays_black=True))