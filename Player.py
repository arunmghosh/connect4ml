class Player:
    id = 0

    def __init__(self, is_user, strategy):
        if is_user:
            self.name = input("What is your name?: ")
        else:
            self.name = Player.id
        Player.id += 1
        self.strategy = strategy  # Strategy object

    def move(self, possible_moves, game):
        return self.strategy.choose_move(possible_moves, game)
