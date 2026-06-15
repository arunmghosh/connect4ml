import pickle


class DeterministicGame:
    def __init__(self, name, players, board_state, filename):
        self.name = name

        # player related attributes
        self.players = players  # array of Player objects
        self.num_players = len(players)
        self.current_player = 0  # player moving, index

        # game status attributes
        self.game_finished = False  # finished = True
        self.board_state = board_state  # where moves are in the array
        self.result = "message overridden in child class"

        # storing game data
        self.filename = filename
        try:
            with open(self.filename, "rb") as f:
                self.recorded_positions = pickle.load(f)
        except FileNotFoundError:
            self.recorded_positions = {}  # table to store game data in

    # player related methods
    def switch_turn(self):
        self.current_player += 1
        self.current_player = self.current_player % self.num_players

    # game status related methods
    def get_possible_moves(self):
        return self.board_state  # override in child classes

    def update_grid(self, move):
        self.board_state = move  # override in child classes

    def update_status(self):
        if not self.get_possible_moves():
            self.game_finished = True

    def update_result(self, msg: str):
        self.result = msg

    # data collection related methods
    def encode(self):
        return self.board_state  # override in child classes
        # new positions will be added to the transposition table

    def export_new_data(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.recorded_positions, f)

    # gameplay mechanic
    def play_game(self):
        while not self.game_finished:
            move = self.players[self.current_player].move(self.get_possible_moves())
            self.update_grid(move)
            self.update_status()
            self.switch_turn()
        print(self.result)
        self.export_new_data()
