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
        self.player_tokens = np.array(["R", "Y"])
        self.col_heights = np.array([0, 0, 0, 0, 0, 0, 0], dtype=int)

        # search board
        self.pointer = ""  # stores color of streak being analyzed, will store winner if 4-streak found
        self.current_streak = 0
        self.traversal_steps = 0  # tracks how much of a row, column or diagonal has been checked

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

    @staticmethod
    def arithmetic_sequence_found(arr, factor, length):
        # given an unsorted list of integers, search for an arithmetic sequence
        # length is the number of terms we want
        # factor is the difference between consecutive terms

        stop_point = max(arr)  # find max value of the list to bound search
        seq = []  # stores sequence we are building

        # check all equivalence classes mod [factor]
        for e in range(factor):
            pointer = e  # element we're looking for in the list
            while pointer <= stop_point:
                if pointer in arr:
                    if len(seq) == 0:  # start point needs to be in the correct section of grid
                        if factor == 6:  # streak is going to the left
                            if pointer % 7 > 2:  # start in center or right section of the grid
                                seq.append(pointer)
                            else:
                                pass
                        elif factor % 7 == 1:  # streak is going to the right
                            if pointer % 7 < 4:  # start in center or left section of the grid
                                seq.append(pointer)
                            else:
                                pass
                        else:  # streak is vertical, so we don't care where it starts
                            seq.append(pointer)
                    else:
                        seq.append(pointer)
                        if len(seq) == length:  # completed the sequence
                            return seq
                else:
                    seq.clear()
                pointer += factor

        return None  # didn't find the sequence

    @staticmethod
    def get_blockages(buffer_space, opp_mask, prev_space, h, factor):
        # if h is 0, we're checking buffer next to the start of the streak, end if 1
        blockages = 0.0  # tracks if buffer spaces are not open

        vertical_bound = 0 - (h * 41)
        direct = 1 - (2 * h)
        factor_six_spillover_col = 6 * (1 - h)  # opposite edge as other streaks
        other_spillover_col = 6 * h

        if buffer_space * direct >= vertical_bound:  # check if we've crossed top or bottom of grid
            if factor == 6:
                if prev_space % 7 == factor_six_spillover_col:  # edge case
                    blockages += 1.0
            elif factor != 7 and prev_space % 7 == other_spillover_col:
                blockages += 1.0

            # check if opponent occupies buffer
            elif buffer_space in opp_mask:
                blockages += 1.0

        return blockages

    # determining game status
    def has_streak(self, player, length, fork):
        buffer = 4 - length  # if we find a streak of 3, need an open space to get 4
        # fork is True if we need a buffer on both sides
        mask = self.player_masks[player]
        opp_mask = self.player_masks[(player + 1) % 2]

        # horizontal streak is consecutive numbers
        # vertical streak is consecutive numbers equivalent mod 7
        # bottom right to top left diagonal is consecutive numbers equivalent mod 6
        # bottom left to top right diagonal is consecutive numbers equivalent mod 8
        streak_types = [1, 7, 6, 8]

        for t in range(len(streak_types)):
            factor = streak_types[t]
            streak = self.arithmetic_sequence_found(mask, factor, length)
            if streak:
                if buffer == 0:  # streak is already a four in a row
                    return True

                # if streak is less than 4, check that the buffer spaces are open

                # first check the low index buffer space (next to start of streak)
                low_buffer = min(streak) - factor
                blockages = self.get_blockages(low_buffer, opp_mask, min(streak), 0, factor)

                if buffer == 2:
                    if blockages == 0.0:
                        low_low_buffer = low_buffer - factor
                        blockages += 0.25 * self.get_blockages(low_low_buffer, opp_mask, low_buffer, 0, factor)
                    else:
                        # consider it blocked because the streak was already blocked before this cell
                        blockages += 0.25

                if fork:  # blocked on one side and we needed both sides open
                    return blockages < 1.0

                # check the high index buffer space
                high_buffer = max(streak) + factor

                # need to keep track of this individual blockage if we need high and high-high buffers to be open
                high_block = self.get_blockages(high_buffer, opp_mask, max(streak), 1, factor)
                blockages += high_block

                if buffer == 1:
                    if fork:
                        return blockages < 1.0
                    return blockages < 2.0

                # buffer == 2
                high_high_buffer = high_buffer + factor
                if high_block == 0.0:
                    blockages += 0.25 * self.get_blockages(high_high_buffer, opp_mask, high_buffer, 1, factor)
                else:
                    # consider it blocked because the streak was already blocked before this cell
                    blockages += 0.25

                if fork:
                    return blockages < 0.5
                return blockages < 1.5  # will be at most 1.25 if only one side is blocked

    def get_possible_moves(self):
        # first check for a four in a row, and return an empty list if found
        if self.has_streak(0, 4, False):
            return []
        if self.has_streak(1, 4, False):
            return []

        # now check if there are any columns with open slots
        open_slots = []
        for col in range(7):
            if self.col_heights[col] < 6:
                open_slots.append(col)
        return open_slots

    def determine_outcome(self):
        if self.pointer == "R":
            self.update_result(self.players[0] + " wins!")
        elif self.pointer == "Y":
            self.update_result(self.players[1] + " wins!")
        else:
            self.update_result("Draw.")

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
        if self.has_streak(player, 4, False):
            return True

        # check if there is a three in a row with an open slot to get to 4
        if self.has_streak(player, 3, False):
            return True

        # check if there is a two in a row with the chance of creating a fork
        if self.has_streak(player, 2, True):
            return True

        return False

    def evaluate_win_chance(self, player):
        score = 0

        if player == self.current_player:
            # player is about to move, check for 2-streak open in one direction
            if self.has_streak(player, 2, False):
                score += 100

        else:  # player is not about to move, check if they have a winning move opponent must block
            if self.has_streak(player, 3, False):
                score += 100

        return score

    # analysis mechanics
    def __copy__(self):
        game = super().copy()
        game.col_heights = self.col_heights.copy()
        return game

    def undo_move(self):
        super().undo_move()
        self.col_heights[self.prev_move] -= 1
        self.board_state[self.col_heights[self.prev_move]] = ""  # empty last occupied cell
