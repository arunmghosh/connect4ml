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

        # analysis tools
        self.analysis_board = board_state  # decoy board so we don't mess up real board when analyzing positions
        self.analysis_turn = self.current_player
        self.prev_move = 0  # will only be stored when using the analysis board

        # storing game data
        self.player_masks = self.player_masks = [[] for _ in range(self.num_players)]  # will keep lists of player moves
        for i in range(self.num_players):
            self.player_masks[i] = []
        self.filename = filename
        try:
            with open(self.filename, "rb") as f:
                self.recorded_positions = pickle.load(f)
        except FileNotFoundError:
            self.recorded_positions = dict()  # dictionary to store game data in

    # player related methods
    def switch_turn(self, player_pointer):
        player_pointer += 1
        player_pointer = player_pointer % self.num_players

    # game status related methods
    def get_possible_moves(self, board):
        return []  # override in child classes

    def get_board_state(self):
        return self.board_state

    def update_board(self, move, board):
        pass  # override in child classes

    def update_mask(self, move):
        self.player_masks[self.current_player].append(move)

    def update_status(self):
        if not self.get_possible_moves(self.board_state):
            self.game_finished = True

    def update_result(self, msg: str):
        self.result = msg

    # minimax helper
    def copy_pos(self):
        self.analysis_board = self.board_state.copy()

    def get_decoy_board(self):
        return self.analysis_board

    def get_trans_table(self):
        return self.recorded_positions

    def get_analysis_turn(self):
        return self.analysis_turn

    def set_prev_move(self, move):
        self.prev_move = move

    def undo_move(self, board):
        pass  # override in child classes

    # heuristic helper
    def score_current_pos(self, board):
        return 0
        # override in child classes
        # will return a heuristic evaluation of the current position

    # data collection related methods
    def encode(self, board):
        return 0 # override in child classes
        # new positions will be added to the transposition table

    def export_new_data(self):
        with open(self.filename, "wb") as f:
            pickle.dump(self.recorded_positions, f)

    # gameplay mechanic
    def play_game(self):
        while not self.game_finished:
            move = self.players[self.current_player].move(self.get_possible_moves(self.board_state), self)
            self.update_board(move, self.board_state)
            self.update_mask(move)
            self.update_status()
            self.switch_turn(self.current_player)
        print(self.result)
        self.export_new_data()
