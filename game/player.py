import tensorflow as tf
from .game_board import GameBoard
from .player_types import *

import logging
import os
import json
import re
from matplotlib import pyplot as plt

def _read_json_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        raise FileNotFoundError(f"Reading failed with error:\n {e}")

class Player:

    def __init__(self, player_type, logger_level = None):

        self.player_type = player_type
        if self.player_type not in config.PLAYER_INFO:
            raise ValueError(f"Player type {player_type} not accepted player")

        self.logger = logging.getLogger("2048_logger")
        logging_level = config.PLAYER_INFO[self.player_type]['logging_level'] if not logger_level else logger_level
        self.logger.setLevel(logging_level)

        stream_handler = logging.StreamHandler()
        self.logger.addHandler(stream_handler)

        self.game_board = GameBoard(logger = self.logger)

        self.max_moves = config.PLAYER_INFO[self.player_type]['max_moves']
        self.num_moves = 0

        self.history_directory = config.PLAYER_INFO[self.player_type]['history_directory']
        if not os.path.exists(self.history_directory):
            os.makedirs(self.history_directory)
            self.logger.debug(f"Created directory {self.history_directory}")

        self.max_version = self._get_max_version()
        self.game_history = tf.zeros((4, 4, self.max_moves), dtype=tf.int64)
        self.move_history = [-1]

        self.move_dict = config.MOVE_DICT
        self.available_moves = list(self.move_dict.values())

    def play_game(self):

        while True:

            self.logger.info(self.game_board)

            if self._game_is_over():
                self._save_game_data()
                self._reset()
                self.logger.info("Thanks for playing!")
                break

            move = config.PLAYER_INFO[self.player_type]['func'](self)

            if move == 'quit':
                self._reset()
                self.logger.info("Thanks for playing!")
                break

            if move not in self.move_dict.values():
                self.logger.warning("Not a recognized move; valid moves are 0,1,2, or 3")
            else:
                valid_move = self.game_board.move(move)

                self.logger.debug(self.game_board)

                if valid_move:
                    self._update_game_info(move)
                else:
                    if self.player_type != 'human':
                        self.available_moves.remove(move)

    def _get_max_version(self, default_val = -1):

        pattern = r'\d+'
        self.logger.debug(f"Getting game info for player {self.player_type}")

        game_list = [entry for entry in os.listdir(self.history_directory) if entry.endswith('.json')]

        if not game_list:
            self.logger.debug(f"No games found in directory {self.history_directory}")
            return 0

        self.logger.debug(f"Found {len(game_list)} games in directory {self.history_directory}")

        game_nums = [int(re.findall(pattern, game)[0]) for game in game_list]
        self.logger.debug(f"Extracted {len(game_nums)} game numbers from game list")

        max_version = max(game_nums)
        self.logger.debug(f"Found max game number {max_version}")

        return max_version

    def _save_game_data(self):

        file_name = self.history_directory + f'game_{self.max_version + 1}.json'
        json_data = self._get_game_metrics()

        try:
            with open(file_name, 'w') as file:
                json.dump(json_data, file)

            self.logger.info(f"Saved file at {file_name}")

        except Exception as e:
            self.logger.critical(f"Saving file {file_name} failed with error\n: {e}")

    def _game_is_over(self):
        return self.game_board.game_over() or self.num_moves == self.max_moves

    def _update_game_info(self, move):

        self.game_history = tf.concat([self.game_history[:, :, :self.num_moves],
                                       self.game_board.board,
                                       self.game_history[:, :, (self.num_moves+1):]],
                                      axis=-1)
        self.num_moves += 1
        self.available_moves = list(self.move_dict.values())
        self.move_history.append(move)

    def _get_game_metrics(self):

        game_metrics = {}

        for name, settings in config.GAME_METRICS.items():
            self.logger.debug(f"Calculating metric {name}")
            metric = settings['func'](self)
            self.logger.debug(f"Returned metric: {metric}")

            game_metrics[name] = metric
        return game_metrics


    def _get_player_game_history(self):

        directory = self.history_directory
        game_list = [os.path.join(directory, entry) for entry in os.listdir(directory) if entry.endswith('.json')]

        num_games = len(game_list)
        self.logger.debug(f"Found {num_games} games in directory {self.history_directory}")
        metric_lists = {name: tf.zeros(num_games, dtype=tf.int32) for name, settings in config.GAME_METRICS.items()
                        if settings["graph"]}

        for i, game in enumerate(game_list):
            data = _read_json_file(game)

            for name, metric_list in metric_lists.items():
                metric_list[i].assign(data[name])

        return metric_lists


    def graph_player_data(self, metric_list, num_bins=30):

        metric_data_dict = self._get_player_game_history()

        for metric in metric_list:

            if metric not in metric_data_dict:
                continue

            data = metric_data_dict[metric]
            self.logger.debug(f"data: {data}")

            if config.GAME_METRICS[metric]['graph'] == 'hist':
                self.logger.debug(f"Generating histogram for {metric} metric")
                plt.hist(data, bins=num_bins, color='skyblue', edgecolor='black')

                # Add labels and title
                plt.xlabel(metric)
                plt.ylabel('Frequency')
                plt.title(f'{metric.capitalize()} Histogram')

                # Show plot
                plt.show()

            elif config.GAME_METRICS[metric]['graph'] == 'bar':
                self.logger.debug(f"Generating bar chart for {metric} metric")
                unique_elements, counts = tf.unique(data)
                unique_elements = tf.strings.as_string(unique_elements.numpy())

                # Create bar chart
                plt.bar(unique_elements, counts, color='skyblue')

                # Add labels and title
                plt.xlabel(metric)
                plt.ylabel('Frequency')
                plt.title(f'{metric.capitalize()} Bar Chart')

                # Show plot
                plt.show()



    def _set_game_board(self, board):
        self.game_board.board = tf.convert_to_tensor(board, dtype=tf.int16)


    def _reset(self):
        self.game_board = GameBoard(logger=self.logger)
        self.game_history = tf.zeros((self.max_moves, 4, 4), dtype=tf.int16)
        self.max_version = self._get_max_version()
        self.num_moves = 0
