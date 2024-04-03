import tensorflow as tf
from config import config
import logging
import pdb


class GameBoard:

    def __init__(self, logger=None):

        self.board = tf.zeros((4, 4, 1), dtype=tf.int64)
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
        for i in range(self.board.shape[0]):
            board_string += "\n   -    -    -    -  \n"
            row_str = "|"
            for j in range(self.board.shape[1]):
                square_str = str(self.board[i, j, 0].numpy())
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

                row_str += before + self.color_codes[self.board[i, j, 0].numpy()] + square_str + self.color_codes[0] + after
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
        if move not in [0, 1, 2, 3]:
            raise ValueError("Not a valid move - valid move is 0, 1, 2, or 3")

        original_board = tf.identity(self.board)

        for _ in range(move):
            original_board = tf.image.rot90(original_board)

        new_board = self._execute_move(original_board)
        for _ in range(4 - move):
            new_board = tf.image.rot90(new_board)

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

        if tf.reduce_any(tf.equal(self.board, 2048)):
            self.logger.critical("2048 - You Won!")
            return True

        if not tf.reduce_all(tf.not_equal(self.board, 0)):
            return False

        copy_board = tf.identity(self.board)
        if tf.reduce_all(tf.equal(copy_board, self._execute_move(copy_board))):
            copy_board = tf.image.rot90(copy_board)
            if tf.reduce_all(tf.equal(copy_board, self._execute_move(copy_board))):
                copy_board = tf.image.rot90(copy_board)
                if tf.reduce_all(tf.equal(copy_board, self._execute_move(copy_board))):
                    copy_board = tf.image.rot90(copy_board)
                    if tf.reduce_all(tf.equal(copy_board, self._execute_move(copy_board))):
                        self.logger.info("No more moves - You Lose!")
                        return True

        return False

    def new_number_generation(self):
        """
        Generate a new number at the beginning of new turn
        Only generates a new number in an empty space
        """
        new_number = (tf.random.uniform((), dtype=tf.int64, maxval=2, seed=None) + 1) * 2  # Randomly choose 2 or 4

        # Get the indices of empty cells in the board
        indices = tf.where(tf.equal(self.board, 0))

        # Randomly choose an index from the list of empty cells
        index = tf.random.uniform((), dtype=tf.int32, maxval=tf.shape(indices)[0], seed=None)
        array_index = tf.gather_nd(indices, [index])

        # Update the board tensor with the new number at the chosen index
        self.board = tf.tensor_scatter_nd_update(self.board, [array_index], [new_number])

    def _execute_move(self, board):

        new_board = tf.zeros_like(board, dtype=tf.int64)

        for j in range(board.shape[1]):

            column = board[:, j, :][:,0]

            non_zero_indices = tf.where(column != 0)[:, 0]
            non_zero_values = tf.gather(column, non_zero_indices)

            new_column = tf.zeros_like(column, dtype=tf.int64)

            for k in range(4):
                num, non_zero_values = self._compress_column(non_zero_values)
                new_column = tf.tensor_scatter_nd_update(new_column, [[k]], num)

            new_column_expanded = tf.expand_dims(new_column, axis=1)
            new_column_expanded = tf.expand_dims(new_column_expanded, axis=2)
            new_board = tf.concat([new_board[:, :j, :], new_column_expanded, new_board[:, j+1:, :]], axis=1)

        return new_board

    def _board_has_not_moved(self, new_board):
        return tf.reduce_all(tf.equal(self.board, new_board))

    @staticmethod
    def _compress_column(column):

        if tf.shape(column)[0] == 0:
            return tf.constant([0], dtype=tf.int64), tf.constant([], dtype=tf.int64)

        elif tf.shape(column)[0] == 1:
            return tf.expand_dims(column[0], axis=0), tf.constant([], dtype=tf.int64)

        else:
            if column[0] == column[1]:
                return tf.expand_dims(column[0] + column[1], axis=0), column[2:]
            else:
                return tf.expand_dims(column[0], axis=0), column[1:]

