from src.core.game import Game
from src.utils.arg_parser import parse_arguments

if __name__ == "__main__":
    args = parse_arguments()
    game = Game(ghost_speed = args.ghost_speed, initial_volume = args.volume)
    game.run()