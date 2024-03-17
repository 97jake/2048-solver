import argparse
import logging

from config import config

def main():

    # Create argument parser
    parser = argparse.ArgumentParser(description='2048 Argument Parser')

    # Add arguments
    parser.add_argument('-p', '--player', choices=config.PLAYER_INFO.keys(),
                        help='Player type (defined in config file)', required=True)
    parser.add_argument('-l', '--log-level', choices=config.LOGGING_LEVELS.keys(), default='info',
                        help='Set the logging level (default: %(default)s)', required=False)

    # Parse arguments
    args = parser.parse_args()

    if args.player not in config.PLAYER_INFO:
        raise ValueError(f"Player type {args.player} is not defined! Check player info dictionary for defined player types")

    player = config.PLAYER_INFO[args.player]["class"](logger_level=config.LOGGING_LEVELS[args.log_level])

    player.play_game()


if __name__ == '__main__':
    main()
