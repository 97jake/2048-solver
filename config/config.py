from game.player_types import *
import logging
import tensorflow as tf

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

# File Paths
base_dir = './data/'
HISTORY_DIR = base_dir + 'game_history/'

# Player Settings - New Players get added here!
PLAYER_INFO = {
    "human": {
        "max_moves": 100000,
        "logging_level": "info",
        "history_directory": HISTORY_DIR + "human/",
        "func": human_make_move
    },
    "bot_v1": {
        "max_moves": 500,
        "logging_level": "warning",
        "history_directory": HISTORY_DIR + "bot/v1/",
        "func": bot_v1_make_move
    },
    "bot_v2": {
        "max_moves": 500,
        "logging_level": "warning",
        "history_directory": HISTORY_DIR + "bot/v2/",
        "func": bot_v2_make_move
    },
    "test": {
        "max_moves": 5,
        "logging_level": "debug",
        "history_directory": HISTORY_DIR + "test/",
        "func": None
    }
}

# Game Board Settings
GAME_COLORS = {
    0: "\033[0m",     # default
    2: "\033[32m",    # yellow
    4: "\033[33m",    # orange
    8: "\033[34m",    # blue
    16: "\033[35m",   # purple
    32: "\033[36m",   # cyan
    64: "\033[37m",   # white
    128: "\033[38m",  # gray
    256: "\033[38m",  # gray
    512: "\033[38m",  # gray
    1024: "\033[38m", # gray
    2048: "\033[38m"  # gray
}

MOVE_DICT = {
    "up": 0,
    "right": 1,
    "left": 3,
    "down": 2,
    "quit": "quit"
}

LOGGING_LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

"""
Metrics Settings - New Metrics Get Added to Dict and Defined Below

Notes -

Metric settings dict should be of the form
  {
    type: ...
    func: ...
    is_graphable: ...
  }

Metric function should only and must accept player class as an argument

Every metric MUST have an associated function
"""
def _game_metric(player):
    if player.num_moves == player.max_moves:
        total_game_history = player.game_history
    else:
        total_game_history = player.game_history[:player.num_moves + 1]
    return [total_game_history[:,:,i].numpy().tolist() for i in range(tf.shape(total_game_history)[2])]

def _count_metric(player):
    return int(player.num_moves)

def _score_metric(player):
    return int(tf.reduce_sum(player.game_board.board).numpy())

def _max_tile_metric(player):
    return int(tf.reduce_max(player.game_board.board).numpy())

GAME_METRICS = {
    "count": {
        "type": int,
        "func": _count_metric,
        "graph": "hist"
    },
    "score": {
        "type": int,
        "func": _score_metric,
        "graph": "hist"
    },
    "max_tile": {
        "type": int,
        "func": _max_tile_metric,
        "graph": "bar"
    },
    "game": {
        "type": tf.Tensor,
        "func": _game_metric,
        "graph": None
    }
}

# Create a PromptSession instance
session = PromptSession()

# Define key bindings for arrow keys
bindings = KeyBindings()
@bindings.add('up')
def _(event):
    event.app.exit("up")
@bindings.add('down')
def _(event):
    event.app.exit("down")
@bindings.add('left')
def _(event):
    event.app.exit("left")
@bindings.add('right')
def _(event):
    event.app.exit("right")

def read_arrow_key():
    try:
        return session.prompt("Press arrow keys (press 'Ctrl-C' to exit): ", key_bindings=bindings)
    except KeyboardInterrupt:
        print("\nExiting...")
        return 'quit'
