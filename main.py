import argparse

from config import config
from game.player import Player

from tqdm import tqdm

def main():

    # Create argument parser
    parser = argparse.ArgumentParser(description='2048 Argument Parser')

    # Add arguments
    parser.add_argument('-p', '--player', choices=config.PLAYER_INFO.keys(),
                        help='Player type (defined in config file)', required=True)
    parser.add_argument('-l', '--log-level', choices=config.LOGGING_LEVELS.keys(), default=None,
                        help='Set the logging level (default: %(default)s)', required=False)
    parser.add_argument('-r', '--runs', default=1,
                        help='Number of games to play (default: %(default)s)', required=False)

    # Parse arguments
    args = parser.parse_args()

    if args.player not in config.PLAYER_INFO:
        raise ValueError(f"Player type {args.player} is not defined! Check player info dictionary for defined player types")

    log_level = args.log_level if args.log_level else config.PLAYER_INFO[args.player]['logging_level']

    player = Player(player_type=args.player, logger_level = config.LOGGING_LEVELS[log_level])

    for _ in tqdm(range(int(args.runs))):
        player.play_game()


if __name__ == '__main__':
    main()
