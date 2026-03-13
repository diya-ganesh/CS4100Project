class Node:
    def __init__(self, value=None, children=None):
        self.value = value
        self.children = [] if children == None else children



def minimax(node, depth, is_maximizing):
    if depth == 0 or len(node.children) == 0:
        return node.value
    
    if is_maximizing:
        best = float("-inf")
        for child in node.children:
            value = minimax(child, depth - 1, False)
            best = max(best, value)
            
        return best
    else: # is minimizing
        best = float("inf")
        for child in node.children:
            value = minimax(child, depth - 1, True)
            best = min(best, value)   
             
        return best

tree = Node(children=[
    Node(children=[Node(4), Node(5)]),
    Node(children=[Node(3), Node(7)])
])

assert minimax(tree, 3, True) == 4
assert minimax(tree, 3, False) == 5