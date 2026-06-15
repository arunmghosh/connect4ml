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

    def update_grid(self, move):
        # player is the index of the current player
        # move is the column index in which the player places a token

        # find the lowest empty slot in column
        next_slot = self.col_slots_left[move]

        # update board state
        self.board_state[next_slot][move] = self.player_tokens[self.current_player]
        self.col_heights[move] += 1

    def check_for_four(self, row_inc, col_inc, row, col):
        # (row, col) is starting coordinate
        # row_inc and col_inc tell us direction of search

        self.current_streak = 0
        self.traversal_steps = 0
        self.pointer = self.board_state[row][col]  # stores color of current streak
        row_pointer = row
        col_pointer = col

        while self.traversal_steps < 7:
            if row_pointer > 5 or col_pointer > 6:
                return False  # passed the edge of the grid, search complete
            if self.pointer != "":
                if self.board_state[row_pointer][col_pointer] != self.pointer:
                    if self.traversal_steps > 3:
                        return False  # not enough spaces left to get 4 in a row
                    self.pointer = self.board_state[row_pointer][col_pointer]  # switch colors case
                else:
                    self.current_streak += 1
                    if self.current_streak == 4:
                        return True  # token of winner stored in self.pointer
            else:
                if self.traversal_steps > 2:
                    return False  # not enough spaces left to get 4 in a row
                self.current_streak = 0
                self.pointer = self.board_state[row_pointer + row_inc][col_pointer + col_inc]
            row_pointer += row_inc
            col_pointer += col_inc
            self.traversal_steps += 1
        self.pointer = ""  # if the game is over and no 4-streak is found, it's a draw
        return False

    def get_possible_moves(self):
        # first check for a four in a row, and return an empty list if found

        # start with horizontal case
        for row in range(6):
            # if middle of row is empty, impossible to have four in a row
            if self.board_state[row][3] != "":
                if self.check_for_four(0, 1, row, 0):
                    return []

        # now check the vertical
        for col in range(7):
            # if column is not at least 4 pieces high, impossible to have four in a row
            if self.board_state[3][col] != "":
                if self.check_for_four(1, 0, 0, col):
                    return []

        # now check bottom right to top left diagonal
        upper_bound = self.col_heights[6]
        for row in range(0, upper_bound):
            if self.check_for_four(1, -1, row, 6):
                return []
        for col in range(3, 6):
            if self.check_for_four(1, -1, 0, col):
                return []

        # now check bottom left to top right diagonal
        upper_bound = self.col_heights[0]
        for row in range(0, upper_bound):
            if self.check_for_four(1, 1, row, 0):
                return []
        for col in range(1, 4):
            if self.check_for_four(1, 1, 0, col):
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
