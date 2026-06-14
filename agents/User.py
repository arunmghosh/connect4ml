import Strategy


class User(Strategy):
    def __init__(self):
        super().__init__("User")

    @staticmethod
    def choose_move(possible_moves):
        print("Open columns: ", possible_moves)
        choice = input("Your move is: ")
        return int(choice)
