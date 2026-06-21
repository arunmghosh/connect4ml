import pickle


class DeterministicGame:
    def __init__(self, name, players, board_state, filename):
        self.name = name

        # player related attributes
        self.players = players  # array of Player objects, assume there are 2 players
        self.current_player = 0  # player moving, index
        self.player_masks = [[], []]  # lists of player moves

        # game status attributes
        self.game_finished = False  # finished = True
        self.board_state = board_state  # where moves are in the array
        self.winner = None  # index of player if there is a winner, None if there is a draw
        self.result = "Draw."

        # analysis tools
        self.prev_move = 0  # for the sake of backtracking during analysis

        # storing game data
        self.filename = filename
        try:
            with open(self.filename, "rb") as f:
                self.recorded_positions = pickle.load(f)
        except FileNotFoundError:
            self.recorded_positions = dict()  # dictionary to store game data in

    # player related methods
    def switch_turn(self):
        self.current_player += 1
        self.current_player = self.current_player % 2

    # game status related methods
    def get_possible_moves(self):
        return []  # override in child classes

    def update_mask(self, move):
        self.player_masks[self.current_player].append(move)

    def update_board(self, move):
        self.prev_move = move
        self.update_mask(move)

    def update_status(self):
        if not self.get_possible_moves():
            self.game_finished = True

    def update_result(self, msg: str):
        self.result = msg

    def determine_outcome(self):
        if self.winner == 0:
            self.update_result(self.players[0] + " wins!")
        elif self.winner == 1:
            self.update_result(self.players[1] + " wins!")
        # result string is "Draw." by default

    # minimax helper
    def __copy__(self):
        game = DeterministicGame(self.name, self.players, self.board_state, self.filename)
        game.player_masks = self.player_masks.copy()
        game.current_player = self.current_player
        return game
        # add more things in child classes

    def sync(self, game):
        self.board_state = game.board_state.copy()
        self.player_masks = game.player_masks.copy()
        self.current_player = game.current_player
        # add more things in child classes

    def undo_move(self):
        self.player_masks[self.current_player].pop()

    # heuristic helper
    def has_win(self, player):
        return False
        # override in child classes

    def evaluate_win_chance(self, player):
        return 0
        # override in child classes

    def score_current_pos(self):
        # positive is good for player 1
        # check if current player has a win
        if self.has_win(self.current_player):
            # 100000 if player 1, -100000 if player 2
            return 100000 - (self.current_player * 200000)

        # check if next player has a win
        next_player = (self.current_player + 1) % 2
        if self.has_win(next_player):
            return -100000 + (self.current_player * 200000)

        # if neither player wins immediately, count their chances to win
        return self.evaluate_win_chance(self.current_player) - self.evaluate_win_chance(next_player)

    # data collection related methods
    def encode(self):
        return 0 # override in child classes
        # new positions will be added to the transposition table

    def logged_current_pos(self):
        return self.encode() in self.recorded_positions

    def export_new_data(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.recorded_positions, f)

    # gameplay mechanic
    def play_game(self):
        while not self.game_finished:
            move = self.players[self.current_player].move(self.get_possible_moves(), self)
            self.update_board(move)
            self.update_status()
            self.switch_turn()
        self.determine_outcome()
        print(self.result)
        self.export_new_data()
