import pygame
import sys
import chess

TILE = 80
BOARD_SIZE = TILE * 8
WHITE_TILE = (245, 235, 215)
DARK_TILE = (75, 115, 70)
PIECE_RADIUS = TILE // 2 - 6
WHITE_PIECE = (245, 230, 200)
BLACK_PIECE = (90, 60, 35)

pygame.init()
screen = pygame.display.set_mode((BOARD_SIZE, BOARD_SIZE))
pygame.display.set_caption("Chess")
piece_font = pygame.font.SysFont("arial", 32, bold=True)

board = chess.Board()

def draw_board():
    for row in range(8):
        for col in range(8):
            color = WHITE_TILE if (row + col) % 2 == 0 else DARK_TILE
            pygame.draw.rect(screen, color, (col * TILE, row * TILE, TILE, TILE))


def draw_pieces():
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            col = chess.square_file(sq)
            row = 7 - chess.square_rank(sq)
            cx = col * TILE + TILE // 2
            cy = row * TILE + TILE // 2

            is_white = piece.color == chess.WHITE
            fill = WHITE_PIECE if is_white else BLACK_PIECE
            outline = (90, 60, 35) if is_white else (245, 230, 200)
            text_color = (90, 60, 35) if is_white else (245, 230, 200)

            pygame.draw.circle(screen, fill, (cx, cy), PIECE_RADIUS)
            pygame.draw.circle(screen, outline, (cx, cy), PIECE_RADIUS, 2)

            label = chess.piece_name(piece.piece_type)[0].upper()
            if piece.piece_type == chess.KNIGHT:
                label = 'N'
            text = piece_font.render(label, True, text_color)
            screen.blit(text, text.get_rect(center=(cx, cy)))

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    draw_board()
    draw_pieces()
    pygame.display.flip()
    clock.tick(60)