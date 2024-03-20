from config import config
from ..player import Player

class BotV1(Player):

    def __init__(self, logger_level=None):
        super().__init__(player_type = 'bot_v1', logger_level=logger_level)


    def play_game(self):

        while True:

            self.logger.info(self.game_board)

            if self._game_is_over():
                self._save_game_data()
                self._reset()
                self.logger.info("Thanks for playing!")
                break

            move = self._pick_a_move(self.available_moves)

            if move not in self.move_dict.values():
                self.logger.warning("Not a recognized move; valid moves are 0,1,2, or 3")

            else:
                valid_move = self.game_board.move(move)

                self.logger.debug(self.game_board)

                if valid_move:
                    self._update_game_info()
                else:
                    self.available_moves.remove(move)

    def _pick_a_move(self, available_moves):

        return available_moves[0]
