import DeterministicGame
import numpy as np


class ConnectFour(DeterministicGame):

    empty_board = np.empty([5, 6], dtype=str)

    def __init__(self, players, start_player):
        # players is an array of 2 Player objects
        # start_player is the index of the starting player
        # board_state is a 2d array (6 x 7 grid) of strings ("", "R", "Y")
        super().__init__("Connect 4", players, start_player, ConnectFour.empty_board)

        # useful information about the board
        self.player_tokens = np.array(["R", "Y"])
        self.col_slots_left = np.array([6, 6, 6, 6, 6, 6, 6], dtype=int)

    def update_grid(self, move):
        # player is the index of the current player
        # move is the column index in which the player places a token

        # find the lowest empty slot in column
        next_slot = 6 - self.col_slots_left[move]

        # update board state
        self.board_state[next_slot][move] = self.player_tokens[self.current_player]
        self.col_slots_left[move] -= 1

    def check_for_four(self, row_inc, col_inc, row, col):
        # base_units is the number of rows, columns or diagonals
        # row_dir and col_dir are values of incrementation of the pointers row and col (-1, 0, 1)
        # row and col are the coordinates of the starting point in the grid (between (0,0) and (5,6))
        start_color = self.board_state[row][col]
        row_pointer = row
        col_pointer = col
        if start_color != "":
            for i in range(3):
                row_pointer += row_inc
                col_pointer += col_inc
                if self.board_state[row_pointer][col_pointer] != start_color:
                    return False
        return True

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
        upper_bound = 6 - self.col_slots_left[6]
        for row in range(0, upper_bound):
            if self.check_for_four(1, -1, row, 6):
                return []
        for col in range(3, 6):
            if self.check_for_four(1, -1, 0, col):
                return []

        # now check bottom left to top right diagonal
        upper_bound = 6 - self.col_slots_left[0]
        for row in range(0, upper_bound):
            if self.check_for_four(1, 1, row, 0):
                return []
        for col in range(1, 4):
            if self.check_for_four(1, 1, 0, col):
                return []

        # now check if there are any columns with open slots
        open_slots = []
        for col in range(7):
            if self.col_slots_left[col] > 0:
                open_slots.append(col)
        return open_slots
