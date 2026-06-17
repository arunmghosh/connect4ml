import Strategy


class Minimax(Strategy):
    def __init__(self):
        super().__init__("Minimax")

    @staticmethod
    def process_analysis(arr, trans_table, pos_key, base_turn):
        # get stats to update trans table
        best_score = 0
        if base_turn % 2 == 0:
            best_score += max(arr)
        else:
            best_score += min(arr)
        best_move = arr.index(best_score)

        # update trans table
        trans_table[pos_key]["score"] = best_score
        trans_table[pos_key]["best move"] = best_move

        # return the best move
        return best_move

    @staticmethod
    def minimax_helper(game, depth, stop_depth, board, trans_table, base_turn):
        if depth == stop_depth:
            # base case, return heuristic evaluation
            return game.score_current_pos(board)

        # recursive call
        game.switch_turn(game.get_analysis_turn())
        next_moves = game.get_possible_moves(board)
        next_move_evals = []
        for n in range(len(next_moves)):
            game.update_board(next_moves[n], board)
            key = game.encode(board)
            if key in trans_table:
                next_move_evals.append(Minimax.minimax_helper(game, depth + 1, depth + 1, board, trans_table,
                                                              base_turn))
            else:
                next_move_evals.append(Minimax.minimax_helper(game, depth + 1, stop_depth, board, trans_table,
                                                              base_turn))
            game.undo_move(board)

        # choose best rating
        if (base_turn + depth) % 2 == 1:
            return max(next_move_evals)
        return min(next_move_evals)

    @staticmethod
    def choose_move(possible_moves, game):
        # first lookup current position
        pos = game.get_board_state()
        trans_table = game.get_trans_table()
        max_depth = 7
        reeval_depth = 2  # if we got more information, we want to update the transposition table
        board = game.get_decoy_board()
        base_turn = game.get_analysis_turn()  # if 0, max score, if 1, min score

        if pos in trans_table:
            # position has already been evaluated, check heuristic valuations of each immediate child position
            scores = []
            for m in range(len(possible_moves)):
                game.update_board(possible_moves[m], board)
                scores.append(game.score_current_pos(board))
                game.undo_move(board)
            return Minimax.process_analysis(scores, trans_table, pos, base_turn)

        # new position, trigger evaluation
        move_evals = []
        for m in range(len(possible_moves)):
            game.update_board(possible_moves[m], board)
            key = game.encode(board)
            if key in trans_table:
                move_evals.append(Minimax.minimax_helper(game, 1, reeval_depth, board, trans_table, base_turn))
            else:
                move_evals.append(Minimax.minimax_helper(game, 1, max_depth, board, trans_table, base_turn))
            game.undo_move(board)

        # choose best move
        return Minimax.process_analysis(move_evals, trans_table, pos, base_turn)
