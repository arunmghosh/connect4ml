from Strategy import Strategy
import numpy as np
import copy


class Heuristic(Strategy):
    def __init__(self):
        super().__init__("Heuristic")
        self.analysis_game = None  # allocated on first use in child class, copy of game object

    def choose_move(self, possible_moves, game):
        # allocate once on first call
        if self.analysis_game is None:
            self.analysis_game = copy.copy(game)  # already synced to current real state
        else:
            self.analysis_game.sync(game)

        ratings = np.empty(len(possible_moves), dtype=int)
        for m in range(len(possible_moves)):
            self.analysis_game.update_board(possible_moves[m])
            ratings[m] = self.analysis_game.score_current_pos()
            self.analysis_game.undo_move()

        return possible_moves[ratings.argmax()]
