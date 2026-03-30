import random 
import sys
sys.path.insert(0, '..')

from board import Board

OPENING_BOOK = {
    # White start
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -":
        ["e2e4", "d2d4", "c2c4", "b1c3", "g1f3", "f2f4", "e2e3"],
    
    # After e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq -":
        ["e7e5", "c7c5", "e7e6", "c7c6", "d7d5", "g8f6", "d7d6", "b8c6"],

    # After d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq -":
        ["d7d5", "g8f6", "e7e6", "c7c5", "f7f5", "c7c6", "b8c6"],

    # After c4
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq -":
        ["e7e5", "c7c5", "g8f6", "e7e6", "c7c6", "d7d5"],

    # After Nf3
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq -":
        ["d7d5", "g8f6", "c7c5", "e7e6", "b8c6"],

    # After Nc3
    "rnbqkbnr/pppppppp/8/8/8/2N5/PPPPPPPP/R1BQKBNR b KQkq -":
        ["d7d5", "e7e5", "g8f6", "c7c5"],

    # After f4
    "rnbqkbnr/pppppppp/8/8/5P2/8/PPPPP1PP/RNBQKBNR b KQkq -":
        ["d7d5", "g8f6", "e7e5", "c7c5"],

    # After e3
    "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq -":
        ["d7d5", "e7e5", "c7c5", "g8f6"]
}

def get_opening_move(board):
    fen_key = " ".join(board.fen().split()[:4]) # ignore move counters
    moves = OPENING_BOOK.get(fen_key)
    if moves:
        uci = random.choice(moves)
        return board.uci_to_move(uci)
    return -1

# Useage:
board = Board()
print(board.move_to_uci(get_opening_move(board)))
