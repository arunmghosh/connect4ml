class DeterministicGame:
    def __init__(self, name, players, start_player, board_state):
        self.name = name
        self.players = players  # array of Player objects
        self.num_players = len(players)
        self.current_player = start_player  # player moving, index
        self.game_finished = False  # finished = True
        self.board_state = board_state  # where moves are in the array

    def switch_turn(self):
        self.current_player += 1
        self.current_player = self.current_player % self.num_players

    def get_possible_moves(self):
        return self.board_state  # override in child classes

    def update_grid(self, move):
        self.board_state = move  # override in child classes

    def update_status(self):
        if not self.get_possible_moves():
            self.game_finished = True

    def play_game(self):
        while not self.game_finished:
            move = self.current_player.move(self.get_possible_moves())
            self.update_grid(move)
            self.update_status()
            self.switch_turn()
