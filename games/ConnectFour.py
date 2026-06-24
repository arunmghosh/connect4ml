import DeterministicGame
import numpy as np


class ConnectFour(DeterministicGame):

    empty_board = np.empty([5, 6], dtype=str)

    def __init__(self, players):
        # players is an array of 2 Player objects
        # start_player is the index of the starting player
        # board_state is a 2d array (6 x 7 grid) of strings ("", "R", "Y")
        super().__init__("Connect 4", players, ConnectFour.empty_board, "connect_4_transposition.pkl")

        # useful information about the board
        self.min_board_ind = 0
        self.max_board_ind = self.min_board_ind + (len(self.board_state) * len(self.board_state[0])) - 1
        self.player_tokens = np.array(["R", "Y"])
        self.col_heights = np.array([0, 0, 0, 0, 0, 0, 0], dtype=int)

        # search board
        self.current_streak = 0
        self.traversal_steps = 0  # tracks how much of a row, column or diagonal has been checked
        self.streak_types = [1, 7, 6, 8]
        # horizontal streak is consecutive numbers
        # vertical streak is consecutive numbers equivalent mod 7
        # bottom right to top left diagonal is consecutive numbers equivalent mod 6
        # bottom left to top right diagonal is consecutive numbers equivalent mod 8

    # turn mechanics
    def update_board(self, move):
        # player is the index of the current player
        # move is the column index in which the player places a token

        # find the lowest empty slot in column
        next_slot = self.col_heights[move]

        # update board state
        self.board_state[next_slot][move] = self.player_tokens[self.current_player]
        self.col_heights[move] += 1
        super().update_board()

    def update_mask(self, move):
        cell_id = move + (self.col_heights[move] * 7)
        self.player_masks[self.current_player].append(cell_id)

    # determining game status
    def cell_in_grid(self, cell: int):
        return self.min_board_ind <= cell <= self.max_board_ind

    def cell_is_reachable(self, cell: int):
        col = cell % 7
        row = (cell - col) / 7
        return row == self.col_heights[col] + 1  # True if cell is empty and right above highest cell in column

    def num_steps_possible(self, num_steps: int, start_cell: int, vert_inc, hor_inc):
        # check if index of cell three steps up or down is in the grid
        # vert_inc is 1 if up, -1 if down, 0 if only checking horizontally
        overflow_col = self.cell_in_grid(start_cell + (7 * vert_inc * num_steps))

        # check if index of cell three steps left or right is in the grid
        # hor_inc is 1 if right, -1 if left, 0 if only checking vertically
        overflow_row = 0 <= (start_cell % 7) + (hor_inc * num_steps) <= 6

        return overflow_row and overflow_col

    def is_seq_possible(self, num_steps: int, factor: int, direction: int, start_cell: int):
        # direction is 1 if forward (index is getting higher), -1 if backward (index is getting lower)
        if factor == 1:  # just a horizontal check
            return self.num_steps_possible(num_steps, start_cell, 0, direction)
        hor_inc = (factor - 7) * direction
        return self.num_steps_possible(num_steps, start_cell, direction, hor_inc)

    def arithmetic_seqs_found(self, arr, opp_arr, factor, length, blanks, straight):
        # given an unsorted list of integers, search for an arithmetic sequence
        # opp_arr is passed to differentiate between blank spaces and spaces occupied by opponent
        # factor is the difference between consecutive terms
        # length is the number of terms we want
        # blanks is the number of blank spaces we're allowed

        stop_point = self.max_board_ind
        seqs = []  # stores sequences we find
        blanks_used = 0

        # check all equivalence classes mod [factor]
        for e in range(factor):
            seq = []  # stores numbers in the current sequence
            pointer = e  # element we're looking for in the list
            while pointer <= stop_point:
                if pointer in arr:
                    if len(seq) == 0:  # start point needs to be in the correct section of grid
                        # check length - 1 steps ahead, always forward
                        if self.is_seq_possible(length - 1, factor, 1, pointer):
                            seq.append(pointer)
                    else:
                        seq.append(pointer)
                elif pointer in opp_arr:  # opponent occupies spot
                    seq.clear()
                    blanks_used = 0
                else:  # spot is blank,
                    if blanks_used == blanks:  # run out of blanks allowed
                        seq.clear()
                        blanks_used = 0
                    elif straight:  # need to make sure we have or can get [length] occupied cells in a row
                        if len(seq) - blanks_used >= length or len(seq) < blanks:
                            seq.append(pointer)
                            blanks_used += 1
                        else:
                            seq.clear()
                            blanks_used = 0
                    else:
                        seq.append(pointer)
                        blanks_used += 1
                if len(seq) == length:  # completed the sequence
                    seqs.append(seq)
                    if seq[0] in arr:  # check if starting point was a blank
                        blanks_used = max(0, blanks_used - 1)
                    seq.pop(0)  # remove first element, see if we can keep moving along this line
                pointer += factor

        return seqs

    def has_streak(self, player, length, fork, straight):
        buffer = 4 - length  # if we find a streak of 3, need an open space to get 4
        # fork is True if we need a buffer on both sides
        # if straight is True, must be [length] cells in a row
        mask = self.player_masks[player]
        opp_mask = self.player_masks[(player + 1) % 2]

        for t in range(len(self.streak_types)):
            factor = self.streak_types[t]
            streaks = self.arithmetic_seqs_found(mask, opp_mask, factor, 4, buffer, straight)
            if len(streaks) > 0:
                if buffer == 0:  # streak is already a four in a row
                    return True

                # if streaks have less than 4 occupied cells, check that the buffer spaces are reachable
                win_threats = 0
                for st in streaks:
                    # check that every cell in the sequence not occupied by the player is reachable
                    unreachable = 0
                    for cell in st:
                        if not (cell in mask or self.cell_is_reachable(cell)):
                            unreachable += 1
                    if unreachable == 0:  # streak can be completed (if buffer > 1 relies on opponent not blocking)
                        win_threats += 1

                    if win_threats >= 1 and not fork:
                        return True
                    if win_threats >= 2:
                        return True

        return False  # no streaks found or could be completed

    def open_grid_spaces(self):
        return 42 - np.sum(self.col_heights)

    def get_possible_moves(self):
        # first check for a four in a row, and return an empty list if found
        if self.has_streak(0, 4, False, True):
            self.winner = 0
            return []
        if self.has_streak(1, 4, False, True):
            self.winner = 1
            return []

        # now check if there are any columns with open slots
        open_slots = []
        for col in range(7):
            if self.col_heights[col] < 6:
                open_slots.append(col)
        return open_slots

    # storing data
    def encode(self):
        pos_id = 0
        for m in self.player_masks[0]:
            pos_id += 2**m

        heights_id = 0
        for h in range(7):
            heights_id += (100 ** h) * (2 ** self.col_heights[h])

        pos_id += (2 ** 42) * heights_id
        return pos_id

    def has_win(self, player):
        # assume player is about to move
        # return True if it is possible to get 4 in a row immediately
        # also True if a fork can be created (3 in a row with 2 ways to get to 4, can't block both)

        # must check if player already has 4 in a row
        if self.has_streak(player, 4, False, True):
            return True

        # check if there is a three in a row with an open slot to get to 4
        if self.has_streak(player, 3, False, False):
            return True

        # check if there is a two in a row with the chance of creating a fork
        if self.has_streak(player, 2, True, True):
            return True

        return False

    def evaluate_win_chance(self, player):
        score = 0
        mask = self.player_masks[self.current_player]
        opp_mask = self.player_masks[(self.current_player + 1) % 2]

        if player == self.current_player:
            # player is about to move, check for 2-streak open in one direction
            for st in self.streak_types:
                current_options = self.arithmetic_seqs_found(mask, opp_mask, st, 4, 2, True)
                score += 100 * current_options

        else:  # player is not about to move, check if they have a winning move opponent must block
            for st in self.streak_types:
                current_options = self.arithmetic_seqs_found(mask, opp_mask, st, 4, 1, False)
                score += 100 * current_options

        return score

    # analysis mechanics
    def __copy__(self):
        game = super().copy()
        game.col_heights = self.col_heights.copy()
        return game

    def sync(self, game):
        super().sync(game)
        self.col_heights = game.col_heights.copy()

    def undo_move(self):
        super().undo_move()
        self.col_heights[self.prev_move] -= 1
        self.board_state[self.col_heights[self.prev_move]] = ""  # empty last occupied cell
