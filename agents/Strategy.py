import random


class Strategy:
    def __init__(self, name):
        self.name = name

    @staticmethod
    def choose_move(possible_moves, game):
        return random.choice(possible_moves)  # override in child classes
