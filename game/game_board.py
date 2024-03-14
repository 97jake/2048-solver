from config import config
import numpy as np
import logging
import random


class GameBoard:

    def __init__(self, logger = None):

        self.board = np.zeros((4,4), np.int16)
        self.new_number_generation()

        self.color_codes = config.GAME_COLORS

        self.logger = logger
        if not self.logger:
            self.logger = logging.getLogger("2048_logger")
            self.logger.setLevel(logging.INFO)


    def __str__(self):

        """
        Print the board
        """

        board_string = ""
        for i in self.board:
            board_string += "\n   -    -    -    -  \n"
            row_str = "|"
            for j in i:
                square_str = str(j)
                num_digits = len(square_str)
                if num_digits == 1:
                    before = "  "
                    after = "  "
                elif num_digits == 2:
                    before = " "
                    after = "  "
                elif num_digits == 3:
                    before = " "
                    after = " "
                else:
                    before = ""
                    after = " "

                row_str += before + self.color_codes[j] + str(j) + self.color_codes[0] + after
            row_str += "|\n"
            board_string += row_str
        board_string += "   -    -    -    -  "

        return board_string


    def move(self, move):

        """
        Makes a move, valid move is 0,1,2,3
        0 - move tiles up
        1 - move tiles right
        2 - move tiles down
        3 - move tiles left
        """

        self.logger.debug(f"Received move: {move}")
        if move not in [0,1,2,3]:
            raise ValueError("Not a valid move - valid move is 0, 1, 2, or 3")

        original_board = np.copy(self.board)

        for i in range(move):
            original_board = np.rot90(original_board)

        new_board = self._execute_move(original_board)
        for i in range(4 - move):
            new_board = np.rot90(new_board)

        if self._board_has_not_moved(new_board):
            self.logger.info("Invalid move, squares must move!")
            return False

        else:
            self.board = new_board
            self.new_number_generation()
            self.logger.debug(self.board)
            return True


    def game_over(self):

        """
        Verify if game is over or not

        Two options for game to be over
        1. No more empty spaces in board
        2. You have a 2048 tile
        """

        if np.any(self.board == 2048):
            self.logger.critical("2048 - You Won!")
            return True

        if not np.all(self.board != 0):
            return False

        copy_board = np.copy(self.board)
        if np.array_equal(copy_board, self._execute_move(copy_board)):
            copy_board = np.rot90(copy_board)
            if np.array_equal(copy_board, self._execute_move(copy_board)):
                copy_board = np.rot90(copy_board)
                if np.array_equal(copy_board, self._execute_move(copy_board)):
                    copy_board = np.rot90(copy_board)
                    if np.array_equal(copy_board, self._execute_move(copy_board)):
                        self.logger.info("No more moves - You Lose!")
                        return True

        return False


    def new_number_generation(self):
        """
        Generate a new number at the beginning of new turn
        Only generates a new number in an empty space
        """

        rows, columns = np.where(self.board == 0)

        new_number = random.choice([2,4])
        index = random.choice(np.arange(len(rows)))
        array_index = (rows[index], columns[index])

        self.board[array_index] = new_number


    def _execute_move(self, board):

        new_board = np.zeros((4,4), np.int16)

        for j in range(board.shape[1]):

            column = board[:,j]
            new_column = np.zeros_like(column, np.int16)

            non_zero_column = column[column!=0]

            for k in range(4):
                num, non_zero_column = self._compress_column(non_zero_column)
                new_column[k] = num

            new_board[:,j] = new_column

        return new_board

    def _compress_column(self, column):

        if len(column) == 0:
            return 0, []

        elif len(column) == 1:
            return column[0], []

        else:
            if column[0] == column[1]:
                return column[0] + column[1], column[2:]
            else:
                return column[0], column[1:]


    def _board_has_not_moved(self, new_board):
        return np.array_equal(self.board, new_board)