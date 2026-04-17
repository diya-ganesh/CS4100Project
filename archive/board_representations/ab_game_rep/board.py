class Move:
    def __init__(self, start, end, promotion=None):
        self.start = start
        self.end = end
        self.promotion = promotion

    def __str__(self):
        return str(self.start) + " -> " + str(self.end)

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start == other.start and self.end == other.end and self.promotion == other.promotion


class Board:
    def __init__(self):
        self.board = self._create_starting_position()
        self.move_history = []
        self.current_player = "w" # and "b" is standard notation

    def _create_starting_position(self):
        board = []
        board.append(["r", "n", "b", "q", "k", "b", "n", "r"])
        board.append(["p", "p", "p", "p", "p", "p", "p", "p"])
        board.append(["", "", "", "", "", "", "", ""])
        board.append(["", "", "", "", "", "", "", ""])
        board.append(["", "", "", "", "", "", "", ""])
        board.append(["", "", "", "", "", "", "", ""])
        board.append(["P", "P", "P", "P", "P", "P", "P", "P"])
        board.append(["R", "N", "B", "Q", "K", "B", "N", "R"])
        return board

    def piece_at(self, r, c):
        return self.board[r][c]

    def set_piece(self, r, c, piece):
        self.board[r][c] = piece

    def _in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def _color_of(self, piece):
        if piece == "":
            return None
        return "w" if piece.isupper() else "b"

    def _is_team(self, piece, color):
        return piece != "" and self._color_of(piece) == color

    def _is_enemy(self, piece, color):
        piece_color = self._color_of(piece)
        return piece_color is not None and piece_color != color

    def opponent(self, color):
        return "b" if color == "w" else "w"

    def get_legal_moves(self, color):
        return self._get_moves(color)

    def _get_moves(self, color):
        moves = []

        for r in range(8):
            for c in range(8):
                piece = self.piece_at(r, c)

                if self._is_team(piece, color):
                    piece_moves = self._piece_moves(r, c, color)
                    for move in piece_moves:
                        moves.append(move)

        return moves

    def _piece_moves(self, r, c, color):
        piece = self.piece_at(r, c)
        if piece == "":
            return []

        p = piece.lower()

        if p == "p":
            return self._pawn_moves(r, c, color)
        if p == "n":
            return self._knight_moves(r, c, color)
        if p == "b" or p == "r" or p == "q":
            return self._slider_moves(r, c, color, p)
        if p == "k":
            return self._king_moves(r, c, color)

        return []

    def _pawn_moves(self, r, c, color):
        moves = []

        direction = -1 if color == "w" else 1
        start_row = 6 if color == "w" else 1

        nr = r + direction
        nc = c
        if self._in_bounds(nr, nc) and self.piece_at(nr, nc) == "":
            moves.append(Move((r, c), (nr, nc)))

            nr2 = r + 2 * direction # move 2 up is possible if on starting row  
            if r == start_row and self._in_bounds(nr2, nc) and self.piece_at(nr2, nc) == "":
                moves.append(Move((r, c), (nr2, nc)))

        # check to the left / right of the target coordinate for capturing 
        for dc in [-1, 1]:
            nc = c + dc
            if self._in_bounds(nr, nc):
                target = self.piece_at(nr, nc)
                if self._is_enemy(target, color):
                    moves.append(Move((r, c), (nr, nc)))

        return moves

    def _knight_moves(self, r, c, color):
        moves = []

        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                          (1, -2), (1, 2), (2, -1), (2, 1)]

        for dr, dc in knight_offsets:
            nr = r + dr
            nc = c + dc

            if self._in_bounds(nr, nc):
                target = self.piece_at(nr, nc)
                if not self._is_team(target, color):
                    moves.append(Move((r, c), (nr, nc)))

        return moves

    def _slider_moves(self, r, c, color, p):
        moves = []
        directions = []

        if p == "b" or p == "q":
            directions.append((-1, -1))
            directions.append((-1, 1))
            directions.append((1, -1))
            directions.append((1, 1))

        if p == "r" or p == "q":
            directions.append((-1, 0))
            directions.append((1, 0))
            directions.append((0, -1))
            directions.append((0, 1))

        for dr, dc in directions:
            nr = r + dr
            nc = c + dc

            while self._in_bounds(nr, nc):
                target = self.piece_at(nr, nc)

                if self._is_team(target, color):
                    break

                moves.append(Move((r, c), (nr, nc)))

                if target != "":
                    break

                nr += dr
                nc += dc

        return moves

    def _king_moves(self, r, c, color):
        moves = []

        king_offsets = [(-1, -1), (-1, 0), (-1, 1),
                        (0, -1), (0, 1),
                        (1, -1), (1, 0), (1, 1)]

        for dr, dc in king_offsets:
            nr = r + dr
            nc = c + dc

            if self._in_bounds(nr, nc):
                target = self.piece_at(nr, nc)
                if not self._is_team(target, color):
                    moves.append(Move((r, c), (nr, nc)))

        return moves

    def make_move(self, move):
        sr = move.start[0]
        sc = move.start[1]
        er = move.end[0]
        ec = move.end[1]

        moved_piece = self.piece_at(sr, sc)
        captured_piece = self.piece_at(er, ec)
        prev_player = self.current_player

        self.move_history.append((move, moved_piece, captured_piece, prev_player))

        self.set_piece(sr, sc, "")
        
        placed_piece = moved_piece
        if move.promotion is not None:
            placed_piece = move.promotion # place whatever the pawn promotes to instead

        self.set_piece(er, ec, placed_piece)

        self.current_player = self.opponent(self.current_player)

    def undo_move(self):
        move, moved_piece, captured_piece, prev_player = self.move_history.pop()

        sr = move.start[0]
        sc = move.start[1]
        er = move.end[0]
        ec = move.end[1]

        self.set_piece(sr, sc, moved_piece)
        self.set_piece(er, ec, captured_piece)

        self.current_player = prev_player

    def is_game_over(self):
        moves = self.get_legal_moves(self.current_player)
        return len(moves) == 0

    def __str__(self):
        rows = []
        for r in range(8):
            row = self.board[r]
            row_string = ""

            for c in range(8):
                piece = row[c]
                if piece == "":
                    row_string += ". "
                else:
                    row_string += piece + " "

            rows.append(row_string)

        result = ""
        for i in range(len(rows)):
            result += rows[i] + "\n"

        return result