from my_jass.mcts.Node import Node

class Tree():
    def __init__(self):
        self.root = Node(None)

    def get_root(self):
        return self.root

