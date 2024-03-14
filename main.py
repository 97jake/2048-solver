import argparse
from config import config

def main():

    # Create argument parser
    parser = argparse.ArgumentParser(description='2048 Argument Parser')

    # Add arguments
    parser.add_argument('--player', help='Player type (defined in config file)', required=True)

    # Parse arguments
    args = parser.parse_args()

    if args.player not in config.PLAYER_INFO:
        raise ValueError(f"Player type {args.player} is not defined! Check player info dictionary for defined player types")

    player = config.PLAYER_INFO[args.player]["class"]()

    player.play_game()


if __name__ == '__main__':
    main()
