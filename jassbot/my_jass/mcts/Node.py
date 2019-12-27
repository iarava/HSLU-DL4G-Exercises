import numpy as np

class Node():
    def __init__(self, card: int):
        if card is None:
            card = None
        self.card = card
        self.nr_played = 0
        self.win = 0
        self.parent = None
        self.childs = []
        self.expanded = False
        self.ucb = 0

    def set_parent(self, parent):
        self.parent = parent

    def add_child(self, child):
        self.childs.append(child)

    def set_expanded(self):
        self.expanded = True

    def get_children(self):
        return self.childs

    def get_parent(self):
        return self.parent

    def get_nr_played(self):
        return self.nr_played

    def get_card(self):
        return self.card

    def get_wins(self):
        return self.win

    def get_expanded(self):
        return self.expanded

    def increase_nr_played(self):
        self.nr_played += 1

    def increase_win(self):
        self.win += 1

    def update_nr_played(self, nr):
        self.nr_played += nr

    def update_wins(self, wins):
        self.win += wins

    def get_child_with_highest_score(self):
        highest_child = self.childs[0]
        for child in self.childs:
            if child.ucb > highest_child.ucb:
                highest_child = child
        return highest_child

    def calculate_ucb(self, n):
        self.ucb = self.win/self.nr_played + 1*np.sqrt(np.log(n)/self.nr_played)

    def check_if_child_exists(self, card):
        exists = False
        for child in self.childs:
            if child.card == card:
                exists = True
        return exists

    def get_child_with_higest_visit(self):
        highest_visit = self.childs[0]
        for child in self.childs:
            if child.nr_played > highest_visit.nr_played:
                highest_visit = child
        return child



