import Strategy


class Minimax(Strategy):
    def __init__(self):
        super().__init__("Minimax")
        self.max_depth = 7
        self.reeval_depth = 2  # if we got more information, we want to update the transposition table
        self.analysis_game = None  # allocated on first use in child class, copy of game object

    def process_analysis(self, arr, pos_key, base_turn):
        # get stats to update trans table
        best_score = 0
        if base_turn % 2 == 0:
            best_score += max(arr)
        else:
            best_score += min(arr)
        best_move = arr.index(best_score)

        # update trans table
        self.analysis_game.trans_table[pos_key]["score"] = best_score
        self.analysis_game.trans_table[pos_key]["best move"] = best_move

        # return the best move
        return best_move

    def minimax_helper(self, depth, stop_depth, base_turn):
        if depth == stop_depth:
            # base case, return heuristic evaluation
            return self.analysis_game.score_current_pos()

        # recursive call
        self.analysis_game.switch_turn()
        next_moves = self.analysis_game.get_possible_moves()
        next_move_evals = []
        for n in range(len(next_moves)):
            self.analysis_game.update_board(next_moves[n])
            if self.analysis_game.logged_current_pos():
                next_move_evals.append(self.minimax_helper(depth + 1, depth + 1, base_turn))
            else:
                next_move_evals.append(self.minimax_helper(depth + 1, stop_depth, base_turn))
            self.analysis_game.undo_move()

        # choose best rating
        if (base_turn + depth) % 2 == 1:
            return max(next_move_evals)
        return min(next_move_evals)

    def choose_move(self, possible_moves, game):
        # allocate once on first call
        if self.analysis_game is None:
            self.analysis_game = game.copy()  # already synced to current real state
        else:
            self.analysis_game.sync(game)

        # first lookup current position
        pos = self.analysis_game.encode()
        base_turn = self.analysis_game.current_player  # if 0, max score, if 1, min score

        if self.analysis_game.logged_current_pos():
            # position has already been evaluated, check heuristic valuations of each immediate child position
            scores = []
            for m in range(len(possible_moves)):
                self.analysis_game.update_board(possible_moves[m])
                scores.append(self.analysis_game.score_current_pos())
                self.analysis_game.undo_move()
            return self.process_analysis(scores, pos, base_turn)

        # new position, trigger evaluation
        move_evals = []
        for m in range(len(possible_moves)):
            self.analysis_game.update_board(possible_moves[m])
            if self.analysis_game.logged_current_pos():
                move_evals.append(self.minimax_helper(1, self.reeval_depth, base_turn))
            else:
                move_evals.append(self.minimax_helper(1, self.max_depth, base_turn))
            game.undo_move()

        # choose best move
        return self.process_analysis(move_evals, pos, base_turn)
