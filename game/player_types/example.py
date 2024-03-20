from config import config
from ..player import Player


"""
This is a template for new player types 

CHANGE
1. player_type attribute passed in to super class
2. _pick_a_move method

_pick_a_move should 
* contain all the logic for the player
* return 0, 1, 2, or 3 (see mapping in config file)

Not meant to be played or edited!
"""
class Example(Player):

    def __init__(self, logger_level=None):
        super().__init__(player_type = 'example', logger_level=logger_level)


    def play_game(self):

        while True:

            self.logger.info(self.game_board)

            if self._game_is_over():
                self._save_game_data()
                self._reset()
                self.logger.info("Thanks for playing!")
                break

            response = self._pick_a_move(self.available_moves)

            if response == "quit":
                self.logger.info("Thanks for playing!")
                self._reset()
                break

            if response not in self.move_dict.values():
                self.logger.warning("Not a recognized move; valid moves are 0,1,2, or 3")

            else:
                move = self.move_dict[response]
                valid_move = self.game_board.move(move)

                self.logger.debug(self.game_board)

                if valid_move:
                    self._update_game_info()
                else:
                    self.available_moves.remove(response)

    def _pick_a_move(self, available_moves):

        #Impliment move logic here

        return 0
