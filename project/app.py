from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from board import Board, WHITE

from evals.base import Evaluator
from evals.material import MaterialEvaluator
from evals.handmade import HandmadeEvaluator

from search.base import SearchResult, Searcher
from search.beam import BeamSearcher
from search.alpha_beta import AlphaBetaSearcher
from search.greedy import GreedySearcher


@dataclass(slots=True)
class BotConfig:
    name: str
    evaluator: Evaluator
    searcher: Searcher
    max_depth: int = 4
    time_limit: float | None = None


@dataclass(slots=True)
class Bot:
    config: BotConfig

    @property
    def name(self) -> str:
        return self.config.name

    def choose_move(self, board: Board) -> SearchResult:
        return self.config.searcher.search(
            board,
            self.config.evaluator,
            max_depth=self.config.max_depth,
            time_limit=self.config.time_limit,
        )


@dataclass(slots=True)
class MatchResult:
    white: str
    black: str
    outcome: str
    moves: int
    terminal: str


@dataclass(slots=True)
class Standing:
    name: str
    points: float = 0.0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    games: int = 0


def default_bots() -> list[Bot]:
    return [
        Bot(BotConfig(
            name="ab-material",
            evaluator=MaterialEvaluator(),
            searcher=AlphaBetaSearcher(),
            max_depth=3,
        )),
        Bot(BotConfig(
            name="beam-material",
            evaluator=MaterialEvaluator(),
            searcher=BeamSearcher(beam_width=10, expand_width=12),
            max_depth=3,
        )),
        Bot(BotConfig(
            name="greedy-material",
            evaluator=MaterialEvaluator(),
            searcher=GreedySearcher(),
            max_depth=1,
        )),
        Bot(BotConfig(
            name="ab-handmade-empty",
            evaluator=HandmadeEvaluator(),
            searcher=AlphaBetaSearcher(),
            max_depth=2,
        )),
    ]


def play_game(white_bot: Bot, black_bot: Bot, max_plies: int = 200) -> MatchResult:
    board = Board()
    plies = 0

    while plies < max_plies:
        draw = board.draw_state()
        if draw:
            return MatchResult(white_bot.name, black_bot.name, "1/2-1/2", plies, draw)

        if board.is_checkmate():
            if board.stm == WHITE:
                return MatchResult(white_bot.name, black_bot.name, "0-1", plies, "checkmate")
            return MatchResult(white_bot.name, black_bot.name, "1-0", plies, "checkmate")

        bot = white_bot if board.stm == WHITE else black_bot
        result = bot.choose_move(board)

        if result.move is None:
            if board.in_check(board.stm):
                if board.stm == WHITE:
                    return MatchResult(white_bot.name, black_bot.name, "0-1", plies, "checkmate")
                return MatchResult(white_bot.name, black_bot.name, "1-0", plies, "checkmate")
            return MatchResult(white_bot.name, black_bot.name, "1/2-1/2", plies, "no legal moves")

        ok = board.make_move(result.move)
        if not ok:
            raise RuntimeError(f"{bot.name} returned an illegal move: {result.move}")

        plies += 1

    return MatchResult(white_bot.name, black_bot.name, "1/2-1/2", plies, "move limit")


def round_robin(
    bots: list[Bot],
    games_per_pair: int = 2,
    max_plies: int = 200,
) -> tuple[list[MatchResult], list[Standing]]:
    standings = {bot.name: Standing(bot.name) for bot in bots}
    results: list[MatchResult] = []

    for a, b in combinations(bots, 2):
        pairings = [(a, b), (b, a)]
        for i in range(games_per_pair):
            white_bot, black_bot = pairings[i % 2]
            result = play_game(white_bot, black_bot, max_plies=max_plies)
            results.append(result)

            white = standings[result.white]
            black = standings[result.black]
            white.games += 1
            black.games += 1

            if result.outcome == "1-0":
                white.points += 1.0
                white.wins += 1
                black.losses += 1
            elif result.outcome == "0-1":
                black.points += 1.0
                black.wins += 1
                white.losses += 1
            else:
                white.points += 0.5
                black.points += 0.5
                white.draws += 1
                black.draws += 1

    ordered = sorted(standings.values(), key=lambda s: (-s.points, -s.wins, s.losses, s.name))
    return results, ordered


def run_arena(
    bots: list[Bot] | None = None,
    *,
    games_per_pair: int = 2,
    max_plies: int = 120,
) -> tuple[list[MatchResult], list[Standing]]:
    if bots is None:
        bots = default_bots()

    results, standings = round_robin(bots, games_per_pair=games_per_pair, max_plies=max_plies)

    print("MATCH RESULTS")
    for result in results:
        print(f"{result.white} vs {result.black}: {result.outcome} ({result.terminal}, {result.moves} plies)")

    print("\nSTANDINGS")
    for standing in standings:
        print(
            f"{standing.name}: {standing.points:.1f} pts | "
            f"W {standing.wins} D {standing.draws} L {standing.losses} | G {standing.games}"
        )

    return results, standings


if __name__ == "__main__":
    run_arena()