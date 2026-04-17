from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from board import Board, WHITE, PIECE_CHARS
from evals.base import Evaluator
from evals.material import MaterialEvaluator
from evals.handmade import HandmadeEvaluator
from search.base import Searcher
from search.greedy import GreedySearcher
from search.alpha_beta import AlphaBetaSearcher
from search.beam import BeamSearcher
from app import Bot, BotConfig


BOT_TIME_LIMIT = 0.10


@dataclass(slots=True)
class SearchSpec:
    name: str
    factory: Callable[[], Searcher]
    max_depth: int
    time_limit: float | None = None


def build_bot_factories() -> dict[str, Callable[[], Bot]]:
    evaluator_specs: list[tuple[str, Callable[[], Evaluator]]] = [
        ("material", MaterialEvaluator),
        ("handmade", HandmadeEvaluator),
    ]

    search_specs = [
        SearchSpec("greedy-d3", lambda: GreedySearcher(), 3),
        SearchSpec("greedy-d4", lambda: GreedySearcher(), 4),
        SearchSpec("ab-d3", lambda: AlphaBetaSearcher(), 3),
        SearchSpec("ab-d4", lambda: AlphaBetaSearcher(), 20),
        SearchSpec("beam-b8-d3", lambda: BeamSearcher(8, 12), 3),
        SearchSpec("beam-b16-d3", lambda: BeamSearcher(16, 24), 3),
        SearchSpec("beam-b8-d4", lambda: BeamSearcher(8, 12), 4),
        SearchSpec("beam-b16-d4", lambda: BeamSearcher(16, 24), 4),
    ]

    factories: dict[str, Callable[[], Bot]] = {}
    for eval_name, eval_factory in evaluator_specs:
        for search_spec in search_specs:
            bot_name = f"{search_spec.name}__{eval_name}"

            def make_bot(
                bot_name: str = bot_name,
                eval_factory: Callable[[], Evaluator] = eval_factory,
                search_factory: Callable[[], Searcher] = search_spec.factory,
                max_depth: int = search_spec.max_depth,
                time_limit: float | None = search_spec.time_limit,
            ) -> Bot:
                return Bot(
                    BotConfig(
                        name=bot_name,
                        evaluator=eval_factory(),
                        searcher=search_factory(),
                        max_depth=max_depth,
                        time_limit=BOT_TIME_LIMIT if time_limit is None else time_limit,
                    )
                )

            factories[bot_name] = make_bot

    return factories


BOT_FACTORIES = build_bot_factories()


UNICODE_PIECES = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}


def print_board(board: Board) -> None:
    print()
    for rank in range(7, -1, -1):
        row = [str(rank + 1)]
        for file in range(8):
            sq = rank * 8 + file
            piece = board.piece[sq]
            if piece == -1:
                row.append(".")
            else:
                ch = PIECE_CHARS[piece]
                row.append(UNICODE_PIECES.get(ch, ch))
        print(" ".join(row))
    print("  a b c d e f g h")
    print()


def list_bots() -> None:
    print("Available bots:")
    for i, name in enumerate(BOT_FACTORIES.keys(), start=1):
        print(f"{i:2d}. {name}")


def choose_bot() -> Bot:
    names = list(BOT_FACTORIES.keys())

    while True:
        list_bots()
        choice = input("\nEnter bot number or exact name: ").strip()

        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(names):
                return BOT_FACTORIES[names[idx]]()

        if choice in BOT_FACTORIES:
            return BOT_FACTORIES[choice]()

        print("Invalid choice.\n")


def choose_color() -> int:
    while True:
        choice = input("Play as white or black? [w/b]: ").strip().lower()
        if choice in {"w", "white"}:
            return WHITE
        if choice in {"b", "black"}:
            return WHITE ^ 1
        print("Invalid choice.")


def human_move(board: Board) -> int:
    legal_moves = board.generate_legal()
    legal_uci = {board.move_to_uci(m): m for m in legal_moves}

    while True:
        move_str = input("Your move (uci, e.g. e2e4): ").strip()

        if move_str == "moves":
            print("Legal moves:")
            print(" ".join(sorted(legal_uci.keys())))
            continue

        if move_str == "quit":
            raise KeyboardInterrupt

        move = legal_uci.get(move_str)
        if move is not None:
            return move

        print("Illegal move. Type 'moves' to list legal moves.")


def result_text(board: Board) -> str:
    draw_reason = board.draw_state()
    if draw_reason:
        return draw_reason
    if board.is_checkmate():
        return "checkmate"
    return "game over"


def main() -> None:
    print("Play against one of your bots.\n")
    bot = choose_bot()
    human_color = choose_color()
    bot_color = human_color ^ 1

    board = Board()
    move_count = 0

    print(f"\nYou are {'White' if human_color == WHITE else 'Black'}")
    print(f"Bot is {bot.name}")
    print("Type 'moves' instead of a move to list legal moves.")
    print("Type 'quit' to exit.")

    while True:
        print_board(board)

        draw_reason = board.draw_state()
        if draw_reason:
            print(f"Draw: {draw_reason}")
            break

        if board.is_checkmate():
            if board.stm == WHITE:
                winner = "Black"
            else:
                winner = "White"
            print(f"Checkmate. {winner} wins.")
            break

        side_name = "White" if board.stm == WHITE else "Black"
        print(f"{side_name} to move.")

        if board.stm == human_color:
            try:
                move = human_move(board)
            except KeyboardInterrupt:
                print("\nGame ended.")
                break

            board.make_move(move)
            move_count += 1
        else:
            print(f"{bot.name} is thinking...")
            result = bot.choose_move(board)

            if result.move is None:
                print(f"{bot.name} returned no move.")
                print(result_text(board))
                break

            move_uci = board.move_to_uci(result.move)
            ok = board.make_move(result.move)
            if not ok:
                print(f"{bot.name} returned illegal move: {move_uci}")
                break

            move_count += 1
            print(
                f"{bot.name} played {move_uci} "
                f"| score={result.score} depth={result.depth_reached} "
                f"nodes={result.nodes} timeout={result.timed_out}"
            )

    print(f"Total plies played: {move_count}")


if __name__ == "__main__":
    main()