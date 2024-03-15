from config import config
from ..player import Player

class Human(Player):

    def __init__(self, logger_level=None):
        super().__init__(player_type = 'human', logger_level=logger_level)


    def play_game(self):

        while True:

            self.logger.info(self.game_board)

            if self._game_is_over():
                self._save_game_data()
                self._reset()
                self.logger.info("Thanks for playing!")
                break

            response = config.read_arrow_key()

            if response == "quit":
                self.logger.info("Thanks for playing!")
                self._reset()
                break

            if response not in self.move_dict:
                self.logger.warning("Not a recognized move; valid moves are up, right, down, or left")

            else:
                move = self.move_dict[response]
                valid_move = self.game_board.move(move)

                self.logger.debug(self.game_board)

                if valid_move:
                    self._update_game_info()