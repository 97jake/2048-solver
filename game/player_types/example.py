from config import config
from ..player import Player


"""
This is a template for new player types 

CHANGE
1. player_type attribute passed in to super class
2. _pick_a_move method
3. __init__.py to import new class to config file
4. Add new player type to PLAYER_INFO dict in config.py 

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

        #Implement move logic here

        return 0
