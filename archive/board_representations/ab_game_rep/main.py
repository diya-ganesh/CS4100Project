from board import Board

b = Board()
print("Initial:")
print(b)

# get all legal moves for the current player
moves = b.get_legal_moves(b.current_player)
print("Number of legal moves for", b.current_player + ":", len(moves))
for move in moves:
    print("Move:", move)
    b.make_move(move)
    print(b)
    b.undo_move()

# so far, these are just pseudo moves