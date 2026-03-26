import chess

from .board import (
    apply_uci_move,
    board_to_strings,
    choose_move_beam,
    create_board,
    evaluate_material,
    legal_moves,
)

SEARCH_DEPTH = 3
BEAM_WIDTH = 4


def main() -> None:
    board = create_board()

    print("Initial board:")
    print(board_to_strings(board))
    print()
    print("FEN:", board.fen())
    print("Turn:", "white" if board.turn == chess.WHITE else "black")
    print("Legal move count:", len(legal_moves(board)))
    print("Material eval for white:", evaluate_material(board, chess.WHITE))

    beam_move, beam_value = choose_move_beam(
        board,
        depth=SEARCH_DEPTH,
        beam_width=BEAM_WIDTH,
    )

    print()
    print("Beam move:", beam_move.uci() if beam_move else None)
    print("Beam value:", beam_value)

    if beam_move is not None:
        apply_uci_move(board, beam_move.uci())
        print()
        print("Board after beam-search move:")
        print(board_to_strings(board))


if __name__ == "__main__":
    main()
