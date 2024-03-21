from config import config

"""
Implement logic for new player types here!

Function should only accept Player class

Function should only return 0,1,2,3 or quit (valid keys in config.MOVE_DICT)
"""

def human_make_move(player):

    move = config.read_arrow_key()

    if move not in player.move_dict.keys() and move != 'quit':
        player.logger.warning(f"{move} is not a recognized move; valid moves are up, left, down, or right")
    return config.MOVE_DICT[move]

def bot_v1_make_move(player):
    return player.available_moves[0]