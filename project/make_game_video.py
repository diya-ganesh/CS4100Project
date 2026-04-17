from __future__ import annotations

import chess
import chess.pgn
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from board import Board, WHITE, PIECE_CHARS
from evals.material import MaterialEvaluator
from evals.handmade import HandmadeEvaluator
from search.greedy import GreedySearcher
from search.alpha_beta import AlphaBetaSearcher
from search.beam import BeamSearcher
from app import Bot, BotConfig


OUTPUT_VIDEO_PATH = "bot_showcase.mp4"
OUTPUT_PGN_PATH = "bot_showcase.pgn"

BOT_TIME_LIMIT = 0.08
MAX_PLIES = 200
FPS = 1

SQUARE_SIZE = 96
MARGIN = 24
SIDEBAR_W = 420
BOARD_SIZE = 8 * SQUARE_SIZE
IMG_W = BOARD_SIZE + SIDEBAR_W + 2 * MARGIN
IMG_H = BOARD_SIZE + 2 * MARGIN

LIGHT = (240, 217, 181)
DARK = (181, 136, 99)
HIGHLIGHT = (246, 246, 105)
BG = (22, 24, 29)
PANEL = (32, 35, 42)
TEXT = (235, 235, 235)
SUBTEXT = (180, 180, 180)

PIECE_TEXT = {
    "P": "P", "N": "N", "B": "B", "R": "R", "Q": "Q", "K": "K",
    "p": "p", "n": "n", "b": "b", "r": "r", "q": "q", "k": "k",
}


BOT_FACTORIES = {
    "ab-d4__handmade": lambda: Bot(BotConfig("ab-d4__handmade", HandmadeEvaluator(), AlphaBetaSearcher(), 4, BOT_TIME_LIMIT)),
    "ab-d3__handmade": lambda: Bot(BotConfig("ab-d3__handmade", HandmadeEvaluator(), AlphaBetaSearcher(), 3, BOT_TIME_LIMIT)),
    "beam-b16-d4__handmade": lambda: Bot(BotConfig("beam-b16-d4__handmade", HandmadeEvaluator(), BeamSearcher(16, 24), 4, BOT_TIME_LIMIT)),
    "beam-b8-d4__handmade": lambda: Bot(BotConfig("beam-b8-d4__handmade", HandmadeEvaluator(), BeamSearcher(8, 12), 4, BOT_TIME_LIMIT)),
    "ab-d4__material": lambda: Bot(BotConfig("ab-d4__material", MaterialEvaluator(), AlphaBetaSearcher(), 4, BOT_TIME_LIMIT)),
    "greedy-d4__handmade": lambda: Bot(BotConfig("greedy-d4__handmade", HandmadeEvaluator(), GreedySearcher(), 4, BOT_TIME_LIMIT)),
}


MATCHES = [
    ("ab-d4__handmade", "beam-b16-d4__handmade"),
    ("ab-d4__handmade", "ab-d4__material"),
    ("beam-b16-d4__handmade", "beam-b8-d4__handmade"),
    ("ab-d3__handmade", "greedy-d4__handmade"),
    ("ab-d4__material", "beam-b8-d4__handmade"),
]


def try_font(size):
    for f in ["arial.ttf", "segoeui.ttf", "DejaVuSans.ttf",
              "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except:
            pass
    return ImageFont.load_default()


FONT_BIG = try_font(34)
FONT_MED = try_font(22)
FONT_SMALL = try_font(18)
FONT_PIECE = try_font(44)


def square_to_xy(sq):
    file = sq & 7
    rank = sq >> 3
    return (
        MARGIN + file * SQUARE_SIZE,
        MARGIN + (7 - rank) * SQUARE_SIZE,
    )


def parse_last_move(uci):
    if not uci:
        return None, None
    f1 = ord(uci[0]) - 97
    r1 = int(uci[1]) - 1
    f2 = ord(uci[2]) - 97
    r2 = int(uci[3]) - 1
    return r1 * 8 + f1, r2 * 8 + f2


def build_history(moves):
    out = []
    for i in range(0, len(moves), 2):
        move = i // 2 + 1
        w = moves[i]
        b = moves[i + 1] if i + 1 < len(moves) else ""
        out.append(f"{move}. {w} {b}".rstrip())
    return out


def draw_frame(board, last_move, ply, move_text, result, white_name, black_name, history):
    img = Image.new("RGB", (IMG_W, IMG_H), BG)
    d = ImageDraw.Draw(img)

    from_sq, to_sq = parse_last_move(last_move)

    # board
    for sq in range(64):
        x, y = square_to_xy(sq)
        f = sq & 7
        r = sq >> 3

        color = LIGHT if (f + r) % 2 == 0 else DARK
        if sq in (from_sq, to_sq):
            color = HIGHLIGHT

        d.rectangle([x, y, x + SQUARE_SIZE, y + SQUARE_SIZE], fill=color)

        piece = board.piece[sq]
        if piece != -1:
            ch = PIECE_CHARS[piece]
            label = PIECE_TEXT[ch]

            box = d.textbbox((0, 0), label, font=FONT_PIECE)
            tx = x + (SQUARE_SIZE - (box[2] - box[0])) / 2
            ty = y + (SQUARE_SIZE - (box[3] - box[1])) / 2 - 4

            fill = (245, 245, 245) if ch.isupper() else (20, 20, 20)
            outline = (20, 20, 20) if ch.isupper() else (240, 240, 240)

            d.text((tx + 1, ty + 1), label, font=FONT_PIECE, fill=outline)
            d.text((tx, ty), label, font=FONT_PIECE, fill=fill)

    # sidebar
    x0 = MARGIN + BOARD_SIZE + 20
    d.rounded_rectangle([x0, MARGIN, IMG_W - MARGIN, IMG_H - MARGIN], radius=12, fill=PANEL)

    y = MARGIN + 16

    # MAIN TITLE
    d.text((x0 + 16, y), "Bot Showcase", font=FONT_BIG, fill=TEXT)
    y += 50

    # SUBFIELDS
    d.text((x0 + 16, y), f"White: {white_name}", font=FONT_MED, fill=TEXT)
    y += 30
    d.text((x0 + 16, y), f"Black: {black_name}", font=FONT_MED, fill=TEXT)
    y += 40

    d.text((x0 + 16, y), f"Ply: {ply}", font=FONT_MED, fill=TEXT)
    y += 30
    d.text((x0 + 16, y), f"Move: {move_text}", font=FONT_MED, fill=TEXT)
    y += 30
    d.text((x0 + 16, y), f"Result: {result}", font=FONT_MED, fill=TEXT)
    y += 40

    for line in history[-22:]:
        d.text((x0 + 16, y), line, font=FONT_SMALL, fill=SUBTEXT)
        y += 20

    return img


def run_game(w_name, b_name):
    white = BOT_FACTORIES[w_name]()
    black = BOT_FACTORIES[b_name]()

    board = Board()
    chess_board = chess.Board()
    game = chess.pgn.Game()

    game.headers["White"] = white.name
    game.headers["Black"] = black.name

    node = game
    moves = []
    frames = []

    frames.append(draw_frame(board, None, 0, "start", "ongoing", w_name, b_name, []))

    ply = 0
    result = "ongoing"

    while ply < MAX_PLIES:
        if board.is_checkmate():
            result = "checkmate"
            break

        player = white if board.stm == WHITE else black
        res = player.choose_move(board)

        if res.move is None:
            result = "no_move"
            break

        uci = board.move_to_uci(res.move)
        move_obj = chess.Move.from_uci(uci)
        san = chess_board.san(move_obj)

        if not board.make_move(res.move):
            result = "illegal"
            break

        chess_board.push(move_obj)
        node = node.add_variation(move_obj)

        moves.append(san)
        ply += 1

        frames.append(draw_frame(
            board, uci, ply, san, "ongoing", w_name, b_name, build_history(moves)
        ))

    game.headers["Result"] = "1/2-1/2" if result != "checkmate" else (
        "1-0" if board.stm != WHITE else "0-1"
    )

    frames.append(draw_frame(
        board, None, ply, "end", result, w_name, b_name, build_history(moves)
    ))

    return frames, game


def main():
    writer = imageio.get_writer(OUTPUT_VIDEO_PATH, fps=FPS, codec="libx264", format="FFMPEG")
    games = []

    try:
        for w, b in MATCHES:
            frames, game = run_game(w, b)
            for f in frames:
                writer.append_data(np.array(f))
            games.append(game)
    finally:
        writer.close()

    with open(OUTPUT_PGN_PATH, "w", encoding="utf-8") as f:
        for g in games:
            print(g, file=f, end="\n\n")

    print("Done:", OUTPUT_VIDEO_PATH, OUTPUT_PGN_PATH)


if __name__ == "__main__":
    main()