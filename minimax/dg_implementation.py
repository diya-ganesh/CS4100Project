import sys
import os
import time # for iterative deepening 
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from board_rep import (
    WP, WN, WB, WR, WQ, WK, BP, BN, BB, BR, BQ, BK, 
    Board, WHITE, BLACK
)


# values in centipawns (looked up online, not sure how accurate they are)
PIECE_VALUES = {
    WP: 100,  WN: 300,  WB: 325,  WR: 500,  WQ: 900,  WK: 100000,
    BP: -100, BN: -300, BB: -325, BR: -500, BQ: -900, BK: -100000,
}

def evaluate(board: Board) -> int:
    """
    +ve = white winning, -ve = black winning.
    """
    score = 0
    for p in board.piece:
        if p != -1:
            score += PIECE_VALUES[p]
    return score

# minimax implementation
def minimax(board: Board, depth: int, alpha: float, beta: float, is_max: bool) -> int:
    """ 
    score is always from white perspective

    alpha: best score white (lower bound)
    beta:  best score black (upper bound)

    prune if branch can't improve on what's been found so far
    """
    # terminal check
    if board.is_checkmate():
        # the side to move is checkmated, so the other side wins
        if board.stm == WHITE:
            return -99999
        else:
            return 99999

    if board.draw_state():
        return 0
    if depth == 0:
        return evaluate(board)

    moves = board.generate_legal()

    if is_max:
        best = float("-inf")
        for m in moves:
            board.make_move(m)
            best = max(best, minimax(board, depth - 1, alpha, beta, False))
            board.unmake_move()
            alpha = max(alpha, best)
            if alpha >= beta:
                break # beta cut-off
        return best
    else:
        best = float("inf")
        for m in moves:
            board.make_move(m)
            best = min(best, minimax(board, depth - 1, alpha, beta, True))
            board.unmake_move()
            beta = min(beta, best)
            if beta <= alpha:
                break # alpha cut-off
        return best

def find_best_move(board: Board, depth: int = 3):
    """
    run minimax for each move and return the best one for the color whose turn it is
    """
    moves = board.generate_legal()
    if not moves:
        return None

    is_white = board.stm == WHITE
    best_move = None
    best_value = float("-inf") if is_white else float("inf")

    for m in moves:
        board.make_move(m)
        value = minimax(board, depth - 1, float("-inf"), float("inf"), not is_white)
        board.unmake_move()

        if is_white and value > best_value: 
            best_value = value
            best_move = m
        elif not is_white and value < best_value:
            best_value = value
            best_move = m

    return best_move

def iterative_deepening_best(board: Board, max_depth: int = 4, time_limit: float = None):
    """
    run minimax for each move; 
    iterative deepening approach that returns the best move within max_depth and time_limit
    """
    best_move = None
    is_white = board.stm == WHITE
    start_time = time.time()
    previous_best = None

    for depth in range(1, max_depth + 1):
        moves = board.generate_legal()
        if not moves:
            return None
        
        current_best_move = None
        best_value = float("-inf") if is_white else float("inf")

        # find the principal variation / pv (best move) 
        # and move it to the front of the list for alpha beta pruning in the next depth level
        if previous_best in moves:
            moves.remove(previous_best)
            moves.insert(0, previous_best)

        for m in moves:
            if time_limit and (time.time() - start_time) > time_limit:
                return best_move

            board.make_move(m)
            value = minimax(board, depth - 1, float("-inf"), float("inf"), not is_white)
            board.unmake_move()

            if is_white and value > best_value: 
                best_value = value
                current_best_move = m
            elif not is_white and value < best_value:
                best_value = value
                current_best_move = m

        if current_best_move:
            best_move = current_best_move
            previous_best = current_best_move
            print(f"Depth {depth}: {board.move_to_uci(best_move)} with evaluation {best_value}")

    return best_move

def play(depth: int = 4):
    board = Board()

    while True:
        print(board)
        print(f"FEN: {board.fen()}")
        print(f"Score: {evaluate(board)}")
        print()

        # check if game over
        draw = board.draw_state()
        if draw:
            print(f"Draw: ({draw})")
            break
        if board.is_checkmate():
            if board.stm == WHITE:
                print("Checkmate! Black wins")
            else:
                print("Checkmate! White wins")
            break
        
        # if game not over, choose a move for the current side
        if board.stm == WHITE:
            side = "White"
        else:
            side = "Black"
        m = iterative_deepening_best(board, depth, 2) # 0.1 for timer is great to see the end game 
        if m is None:
            print(f"No legal moves for {side}")
            break

        print(f"{side} plays: {board.move_to_uci(m)}")
        print()
        board.make_move(m)

if __name__ == "__main__":
    play(depth=6)