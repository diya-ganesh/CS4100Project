import unittest

import chess

from js_board_rep import (
    apply_uci_move,
    board_to_matrix,
    choose_move_beam,
    create_board,
    evaluate_material,
    legal_moves,
)


class JSBoardRepTests(unittest.TestCase):
    def test_starting_board_matrix_has_expected_pieces(self) -> None:
        board = create_board()
        matrix = board_to_matrix(board)

        self.assertEqual(matrix[0], ["r", "n", "b", "q", "k", "b", "n", "r"])
        self.assertEqual(matrix[7], ["R", "N", "B", "Q", "K", "B", "N", "R"])
        self.assertEqual(matrix[3], ["."] * 8)

    def test_apply_uci_move_updates_board_state(self) -> None:
        board = create_board()

        move = apply_uci_move(board, "e2e4")

        self.assertEqual(move.uci(), "e2e4")
        self.assertEqual(board.piece_at(chess.E4).symbol(), "P")
        self.assertIsNone(board.piece_at(chess.E2))
        self.assertEqual(board.turn, chess.BLACK)

    def test_evaluate_material_reflects_capture_balance(self) -> None:
        board = create_board("4k3/8/8/8/8/8/4q3/4K3 w - - 0 1")

        self.assertEqual(evaluate_material(board, chess.WHITE), -9)
        self.assertEqual(evaluate_material(board, chess.BLACK), 9)

    def test_choose_move_beam_returns_legal_move_from_start(self) -> None:
        board = create_board()

        move, value = choose_move_beam(board, depth=2, beam_width=4)

        self.assertIsNotNone(move)
        self.assertIn(move, legal_moves(board))
        self.assertIsInstance(value, float)

    def test_choose_move_beam_finds_forced_mate_in_one(self) -> None:
        board = create_board("6k1/5Q2/6K1/8/8/8/8/8 w - - 0 1")

        move, value = choose_move_beam(board, depth=2, beam_width=4)

        self.assertIsNotNone(move)
        self.assertEqual(value, float("inf"))

        board.push(move)
        self.assertTrue(board.is_checkmate())


if __name__ == "__main__":
    unittest.main()
