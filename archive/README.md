# Archive

Early prototypes and experiments from the development process. These are **not used by the production engine** in `project/` — they're kept for reference.

## Contents

```
archive/
├── board_representations/   # Three independent early board rep prototypes
│   ├── board_rep.py         # Initial flat-array board
│   ├── ab_game_rep/         # Prototype by Anthony Basko
│   ├── dg_game_rep/         # Prototype by Diya Ganesh
│   └── js_game_rep/         # Prototype by John Sargent (includes unit tests)
├── search_algorithms/       # Early search drafts before the modular rewrite
│   ├── minimax.py           # Basic minimax from Anthony
│   ├── minimax/             # Diya Ganesh's minimax initialization
│   └── beam_search.py       # Early beam search draft
└── tests/
    └── test_js_board_rep.py # Unit tests for the John Sargent board prototype
```

The production code evolved from lessons learned here — the final bitboard engine in `project/board.py` replaced all three board prototypes.
