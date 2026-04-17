import chess # TODO: or the board rep we use, hasn't been pushed yet

# class Node:
#     def __init__(self, value=None, children=None):
#         self.value = value
#         self.children = [] if children == None else children
        
board = chess.Board()

# TODO: Placeholder evaluation, needs to be way more accurate to real strategy
def evaluate(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            if piece.color == chess.WHITE:
                score += 1
            else: 
                score -= 1
    
    return score

def minimax(board, depth, is_maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board)
    
    moves = board.legal_moves
    
    if is_maximizing:
        best = float("-inf")
        for move in moves:
            board.push(move)
            value = minimax(board, depth - 1, False)          
            # print(move, value)
            
            board.pop() # undo 
            best = max(best, value)
            
        return best
    else: # is minimizing
        best = float("inf")
        for move in moves:
            board.push(move)
            value = minimax(board, depth - 1, True)
            # print(move, value)
            
            board.pop() # undo
            best = min(best, value)
             
        return best

# Run minimax once for each possible move, and pick the best one 
def choose_move(board, depth):
    best_move = None
    best_value = float("-inf")
    
    moves = board.legal_moves

    for move in moves:
        board.push(move)
        value = minimax(board, depth - 1, False)
        board.pop()

        if value > best_value:
            best_value = value
            best_move = move

    return best_move

# tree = Node(children=[
#     Node(children=[Node(4), Node(5)]),
#     Node(children=[Node(3), Node(7)])
# ])

# assert minimax(tree, 3, True) == 4
# assert minimax(tree, 3, False) == 5

# minimax(board, 3, True)

print(choose_move(board, 3))