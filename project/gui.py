from __future__ import annotations

import sys
import subprocess
import chess
import chess.svg

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel
)
from PyQt6.QtSvgWidgets import QSvgWidget

from app import default_bots
from board import Board

def get_stockfish_eval(fen: str):
    try:
        p = subprocess.Popen(
            ["stockfish"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )

        p.stdin.write(f"position fen {fen}\n")
        p.stdin.write("go depth 10\n")
        p.stdin.flush()

        score = 0

        while True:
            line = p.stdout.readline()
            if "score cp" in line:
                parts = line.split()
                score = int(parts[parts.index("cp") + 1]) / 100
            if "bestmove" in line:
                break

        p.kill()
        return score
    except:
        return None


class ChessGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Chess Bot GUI")

        self.py_board = chess.Board()
        self.engine_board = Board()

        self.bot = default_bots()[0]

        self.auto_play = False

        # layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        # eval labels
        self.left_eval = QLabel("Stockfish: 0")
        self.right_eval = QLabel("Bot: 0")

        # SVG board
        self.svg_widget = QSvgWidget()
        self.svg_widget.setFixedSize(600, 600)

        # buttons
        btn_layout = QVBoxLayout()

        self.undo_btn = QPushButton("Undo")
        self.undo_btn.clicked.connect(self.undo)

        self.bot_btn = QPushButton("Play Bot Move")
        self.bot_btn.clicked.connect(self.play_bot)

        self.toggle_btn = QPushButton("Toggle Auto Bot")
        self.toggle_btn.clicked.connect(self.toggle_auto)

        btn_layout.addWidget(self.left_eval)
        btn_layout.addWidget(self.right_eval)
        btn_layout.addWidget(self.undo_btn)
        btn_layout.addWidget(self.bot_btn)
        btn_layout.addWidget(self.toggle_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.svg_widget)

        # dragging
        self.selected_square = None

        self.svg_widget.mousePressEvent = self.mouse_press
        self.svg_widget.mouseReleaseEvent = self.mouse_release

        self.update_board()


    def update_board(self):
        self.engine_board = Board(self.py_board.fen())

        svg = chess.svg.board(
            self.py_board,
            size=600,
            lastmove=self.py_board.peek() if self.py_board.move_stack else None
        )

        self.svg_widget.load(bytearray(svg, encoding="utf-8"))

        # evals
        bot_eval = self.bot.config.evaluator.evaluate(self.engine_board) / 100
        sf_eval = get_stockfish_eval(self.py_board.fen())

        self.right_eval.setText(f"Bot: {bot_eval:.2f}")
        self.left_eval.setText(f"SF: {sf_eval if sf_eval is not None else 'N/A'}")

        # auto play
        if self.auto_play and self.py_board.turn == chess.BLACK:
            self.play_bot()

    # ---------------- INPUT ----------------

    def square_from_pos(self, x, y):
        size = self.svg_widget.width() // 8
        col = x // size
        row = y // size
        return chess.square(col, 7 - row)

    def mouse_press(self, event):
        self.selected_square = self.square_from_pos(event.x(), event.y())

    def mouse_release(self, event):
        if self.selected_square is None:
            return

        target = self.square_from_pos(event.x(), event.y())

        move = chess.Move(self.selected_square, target)

        if move in self.py_board.legal_moves:
            self.py_board.push(move)

        self.selected_square = None
        self.update_board()

    # ---------------- BUTTONS ----------------

    def undo(self):
        if self.py_board.move_stack:
            self.py_board.pop()
        self.update_board()

    def play_bot(self):
        if self.py_board.is_game_over():
            return

        self.engine_board = Board(self.py_board.fen())
        result = self.bot.choose_move(self.engine_board)

        move = chess.Move.from_uci(self.engine_board.move_to_uci(result.move))
        self.py_board.push(move)

        self.update_board()

    def toggle_auto(self):
        self.auto_play = not self.auto_play



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ChessGUI()
    gui.show()
    sys.exit(app.exec())