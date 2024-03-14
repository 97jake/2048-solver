from .game_board import GameBoard
from config import config

import logging
import os
import json
import numpy as np
import re


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

        self.max_version = self._read_max_version()
        self.game_history = np.zeros((self.max_moves, 4, 4), np.int16)

        self.move_dict = config.MOVE_DICT

    def _read_max_version(self, default_val = -1):

        data = _read_json_file(config.MAX_VERSION_FILENAME)
        self.logger.debug(f"Reading in data: {data}")

        if not data:
            self.logger.warning(f"No data read, returning default value of {default_val}")
            return default_val

        if self.player_type not in data:
            self.logger.warning(f"Player type not found in {config.MAX_VERSION_FILENAME}, returning default value of {default_val}")
            return default_val

        return int(data[self.player_type])


    def _write_max_version(self, new_version = -1, data_overwrite = None):

        if data_overwrite:
            data = data_overwrite
        else:
            data = _read_json_file(config.MAX_VERSION_FILENAME)
            if not isinstance(new_version, int):
                new_version = int(new_version)
            data[self.player_type] = new_version

        with open(config.MAX_VERSION_FILENAME, 'w') as file:
            try:
                json.dump(data, file)
                return data
            except:
                raise ValueError(f"Data {data} failed to write to file {file}")


    def _reset_max_version(self):

        if self.player_type != 'admin':
            self.logger.error(f"Player type {self.player_type} doesn't have permission to use this method!")
            return None

        max_version_data = {}
        pattern = r'\d+'

        for player, settings in self.player_info.items():
            self.logger.debug(f"Getting game info for player {player}")
            directory = settings['history_directory']

            game_list = [entry for entry in os.listdir(directory) if entry.endswith('.json')]

            if not game_list:
                self.logger.debug(f"No games found in directory {directory}")
                max_version_data[player] = 0
                continue

            self.logger.debug(f"Found {len(game_list)} games in directory {directory}")

            game_nums = [int(re.findall(pattern, game)[0]) for game in game_list]
            self.logger.debug(f"Extracted {len(game_nums)} game numbers from game list")

            max_version_data[player] = max(game_nums)
            self.logger.debug(f"Found max game number {max_version_data}")

        self._write_max_version(data_overwrite=max_version_data)
        return max_version_data



    def _save_game_data(self):

        file_name = self.history_directory + f'game_{self.max_version + 1}.json'
        json_data = self._get_game_metrics()

        try:
            with open(file_name, 'w') as file:
                json.dump(json_data, file)

            self.logger.info(f"Saved file at {file_name}")
            self._write_max_version(self.max_version + 1)

        except Exception as e:
            self.logger.critical(f"Saving file {file_name} failed with error\n: {e}")

    def _game_is_over(self):
        return self.game_board.game_over() or self.num_moves == self.max_moves


    def _update_game_info(self):

        self.game_history[self.num_moves] = self.game_board.board
        self.num_moves += 1


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
        metric_lists = {name: np.zeros(num_games) for name,settings in config.GAME_METRICS.items()
                        if settings["is_graphable"]}

        for i,game in enumerate(game_list):
            data = _read_json_file(game)

            for name, metric_list in metric_lists.items():
                metric_list[i] = data[name]

        return metric_list


    def _set_game_board(self, board):
        self.game_board.board = board


    def _reset(self):

        self.game_board = GameBoard(logger = self.logger)
        self.game_history = np.zeros((self.max_moves, 4, 4), np.int16)
        self.max_version = self._read_max_version()
        self.num_moves = 0
