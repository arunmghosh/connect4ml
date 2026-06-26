import random


class Strategy:
    def __init__(self, name):
        self.name = name

    def choose_move(self, possible_moves, game):
        return random.choice(possible_moves)  # override in child classes
