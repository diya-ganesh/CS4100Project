# ChessBot

A modular chess engine in Python that pits pluggable search algorithms and evaluation functions against each other in a round-robin arena — built to empirically compare AI game-playing strategies.

---

## Motivation & Problem Statement

Chess has been used in AI research for decades, providing a fully observable, known, deterministic, and adversarial environment [1]. Despite its simple structure, the state space of this game is huge, containing 1044 legal positions. Therefore exhaustive search is pretty much impossible and requires the use of intelligent pruning and evaluation strategies. Shannon’s pioneering work on computer chess laid the foundation where the mini-max evaluation framework was first proposed, as well as with the trade-off between the search depth and computation cost that the engines after would have to manage [1].

The methods of greedy evaluation, alpha-beta pruning, and constrained searches like beam search each have varying tradeoffs between completeness and efficiency. Modern engines like Stockfish and AlphaZero have outdone classical methods with neural network evaluation and self-play reinforcement learning, with resources that are not widely available [4]. The disparity between high level and classical algorithms inspired our core research question. We wanted to build our very own chess engine from scratch,including a custom board representation, legal moves generation, and evaluation functions, all based solely on classical artificial intelligence methods.

---

## Features

- **Bitboard board representation** with precomputed attack tables (magic bitboards for sliding pieces) and Zobrist hashing for fast, correct position tracking
- **Three search algorithms**: Iterative Deepening Alpha-Beta (with quiescence search & move ordering), Beam Search, and Greedy Search
- **Two evaluators**: a simple material counter and a rich handmade evaluator with 50+ heuristics (pawn structure, king safety, piece activity, endgame scaling)
- **Fully modular design**: any evaluator plugs into any searcher without touching the core engine
- **Round-robin arena** for head-to-head bot comparison with win/draw/loss standings
- **Human vs. Bot CLI** for interactive play (UCI move format)
- **Game video export** — renders match replays as MP4 files with move history sidebar

---

## Installation & Setup

**Requirements**: Python 3.10+

```bash
# Clone the repository
git clone https://github.com/diya-ganesh/CS4100Project.git
cd CS4100Project

# Install dependencies
pip install pygame chess imageio Pillow
```

No package manager configuration file is included; install the four dependencies above directly.

---

## Usage

### Play against a bot (interactive CLI)

```bash
python -m project.botfight
```

You will be shown a bot selection menu. Enter moves in UCI format (e.g., `e2e4`, `g1f3`).

### Run a bot tournament (round-robin arena)

```bash
python -m project.app
```

Runs all configured bot pairings and prints a standings table with wins, draws, losses, and points.

### Generate game replay videos

```bash
python project/make_game_video.py
```

Renders selected match-ups as MP4 files and writes PGN game records alongside them.

---

## Project Structure

```
CS4100Project/
├── project/                    # Main source code
│   ├── board.py                # Bitboard engine: move generation, make/unmake, Zobrist hashing
│   ├── app.py                  # Bot definitions and round-robin arena runner
│   ├── botfight.py             # Interactive human-vs-bot CLI
│   ├── make_game_video.py      # Pygame-based game visualization and MP4 export
│   ├── search/
│   │   ├── base.py             # Abstract Searcher interface
│   │   ├── alpha_beta.py       # Iterative deepening alpha-beta with quiescence search
│   │   ├── beam.py             # Beam search (configurable width and expand width)
│   │   └── greedy.py           # One-move lookahead greedy baseline
│   └── evals/
│       ├── base.py             # Abstract Evaluator interface
│       ├── material.py         # Simple piece-count evaluator
│       └── handmade.py         # Positional evaluator: PST, pawn structure, king safety, etc.
└── archive/                    # Earlier prototypes and alternative implementations
    ├── board_representations/  # Experimental board rep approaches
    ├── search_algorithms/      # Legacy minimax and beam search drafts
    └── tests/                  # Unit tests for archived components
```

---

## Algorithms & Techniques

| Component | Details |
|---|---|
| **Board** | 12 bitboards (one per piece), magic bitboard slider attacks, Zobrist hashing, 3-fold repetition + 50-move rule |
| **Move encoding** | 21-bit packed integers (from/to/promotion/flags) for cheap tree copying |
| **Alpha-Beta** | Iterative deepening, move ordering (best move first), quiescence search to resolve captures |
| **Beam Search** | Breadth-first, keeps top-N positions per layer; configurable `beam_width` and `expand_width` |
| **Greedy** | Evaluates all legal moves one ply deep; minimal-overhead baseline |
| **Material eval** | Pawn=100, Knight=320, Bishop=330, Rook=500, Queen=900 |
| **Handmade eval** | Tapered opening/endgame PST, passed pawns, pawn structure, outposts, rook activity, king safety, threat detection, endgame scaling |

### Available Bot Configurations

Bots are named `<searcher>__<evaluator>`. Examples:

| Bot name | Searcher | Evaluator |
|---|---|---|
| `greedy__material` | Greedy | Material |
| `greedy__handmade` | Greedy | Handmade |
| `ab-d4__material` | Alpha-Beta depth 4 | Material |
| `ab-d4__handmade` | Alpha-Beta depth 4 | Handmade |
| `beam-w8__handmade` | Beam (width 8) | Handmade |
| `beam-w16__handmade` | Beam (width 16) | Handmade |

16 configurations total are defined in [`project/app.py`](project/app.py).

---

## Links

| Resource | Link |
|---|---|
| Executive summary | [Click Here!](https://www.overleaf.com/read/hzrwmgjnpwvs#096c9f) |
| Slides | [Click Here!](https://docs.google.com/presentation/d/1YzX0JNNbyY-okYWrtTwzSI86QNTcKHsskY-NxRFWB-A/edit?usp=sharing) |
| Anthony Basko | [github.com/nunnyu](https://github.com/nunnyu) |
| Diya Ganesh | [github.com/diya-ganesh](https://github.com/diya-ganesh) |
| John Sargent | [github.com/jmsargent10](https://github.com/jmsargent10) |
| Marselis Singh | [github.com/webbometry](https://github.com/webbometry) |

---

## Additional Notes & Project Sources

> **Testing**: The `archive/tests/` directory contains unit tests for early board representation prototypes. There are no automated tests for the production `project/` code; correctness was validated manually via PERFT move-count verification and interactive play.

> **Performance**: All search algorithms enforce a 0.1-second per-move time limit, configurable in [`project/app.py`](project/app.py).

> [1] Shannon, C.E. ”Programming a Computer for Playing Chess.” *Philosophical Magazine*, 41(314), 1950. Foundational mini-max framework; theoretical basis for all search-based chess engines.<br>
[2] Knuth, D.E. and Moore, R.W. ”An Analysis of Alpha-Beta Pruning.” *Artificial Intelligence*, Vol. 6, No. 4, pp. 293–326, 1975. Proves correctness and efficiency bounds for alpha-beta.<br>
[3] Pastukhov, S. ”Playing Board Games with the Predict Results of Beam Search Algorithm.” *arXiv*, 2404.16072, 2024. Applies beam search to two-player board games; evaluates tradeoffs vs. full-tree methods.<br>
[4] Silver, D. et al. ”A General Reinforcement Learning Algorithm that Masters Chess, Shogi, and Go Through Self-Play.” *Science*, 362(6419), 2018. AlphaZero; establishes neural network as contrast to classical search.
