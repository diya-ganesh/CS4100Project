import chess


MoveScore = tuple[float, chess.Move]


PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,
}


def create_board(fen: str | None = None) -> chess.Board:
    return chess.Board() if fen is None else chess.Board(fen)


def legal_moves(board: chess.Board) -> list[chess.Move]:
    return list(board.legal_moves)


def apply_uci_move(board: chess.Board, uci: str) -> chess.Move:
    move = chess.Move.from_uci(uci)
    if move not in board.legal_moves:
        raise ValueError(f"Illegal move: {uci}")

    board.push(move)
    return move


def board_to_matrix(board: chess.Board) -> list[list[str]]:
    rows: list[list[str]] = []

    for rank in range(7, -1, -1):
        row: list[str] = []
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            row.append(piece.symbol() if piece else ".")
        rows.append(row)

    return rows


def board_to_strings(board: chess.Board) -> str:
    return "\n".join(" ".join(row) for row in board_to_matrix(board))


def evaluate_material(board: chess.Board, perspective: chess.Color = chess.WHITE) -> int:
    score = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        value = PIECE_VALUES[piece.piece_type]
        score += value if piece.color == perspective else -value

    return score


def _evaluate_position(board: chess.Board, perspective: chess.Color) -> float:
    if board.is_checkmate():
        return float("-inf") if board.turn == perspective else float("inf")

    if (
        board.is_stalemate()
        or board.is_insufficient_material()
        or board.is_seventyfive_moves()
        or board.is_fivefold_repetition()
    ):
        return 0.0

    return float(evaluate_material(board, perspective))


def _ordered_moves(
    board: chess.Board,
    perspective: chess.Color,
    maximizing: bool,
    beam_width: int | None,
) -> list[MoveScore]:
    scored_moves: list[MoveScore] = []

    for move in board.legal_moves:
        board.push(move)
        score = _evaluate_position(board, perspective)
        board.pop()
        scored_moves.append((score, move))

    scored_moves.sort(key=lambda item: item[0], reverse=maximizing)

    if beam_width is None or beam_width <= 0:
        return scored_moves

    return scored_moves[:beam_width]


def _beam_value(
    board: chess.Board,
    depth: int,
    beam_width: int,
    perspective: chess.Color,
) -> float:
    if depth == 0 or board.is_game_over():
        return _evaluate_position(board, perspective)

    maximizing = board.turn == perspective
    candidate_moves = _ordered_moves(board, perspective, maximizing, beam_width)

    if not candidate_moves:
        return _evaluate_position(board, perspective)

    if maximizing:
        best_value = float("-inf")
        for _, move in candidate_moves:
            board.push(move)
            value = _beam_value(board, depth - 1, beam_width, perspective)
            board.pop()
            best_value = max(best_value, value)
        return best_value

    best_value = float("inf")
    for _, move in candidate_moves:
        board.push(move)
        value = _beam_value(board, depth - 1, beam_width, perspective)
        board.pop()
        best_value = min(best_value, value)

    return best_value


def choose_move_beam(
    board: chess.Board,
    depth: int,
    beam_width: int,
    perspective: chess.Color | None = None,
) -> tuple[chess.Move | None, float]:
    if depth <= 0:
        raise ValueError("depth must be at least 1")
    if beam_width <= 0:
        raise ValueError("beam_width must be at least 1")

    perspective = board.turn if perspective is None else perspective
    best_move = None
    best_value = float("-inf")

    maximizing = board.turn == perspective

    for _, move in _ordered_moves(board, perspective, maximizing, None):
        board.push(move)
        value = _beam_value(board, depth - 1, beam_width, perspective)
        board.pop()

        if best_move is None or value > best_value:
            best_value = value
            best_move = move

    return best_move, best_value
