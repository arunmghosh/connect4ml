import Strategy


class User(Strategy):
    def __init__(self):
        super().__init__("User")

    def choose_move(self, possible_moves, game):
        print("Open columns: ", possible_moves)
        choice = input("Your move is: ")
        return int(choice)
