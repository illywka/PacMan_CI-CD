import argparse
from src.utils.constants import DIFFICULTY_SPEEDS, DEFAULT_VOLUME

def parse_arguments():
    parser = argparse.ArgumentParser(
        description = "Pacman - Налаштування гри",
        formatter_class = argparse.RawDescriptionHelpFormatter,
        epilog = """
            Приклади використання:
                python main.py --difficulty easy
                python main.py --difficulty hard --volume 0.8
                python main.py -d medium -v 0.3
        """)

    parser.add_argument(
        '--difficulty', '-d',
        type = str,
        choices = ['easy', 'medium', 'hard'],
        default = 'medium',
        help = 'Складність гри (easy, medium, hard). За замовчуванням: medium'
    )

    parser.add_argument(
        '--volume', '-v',
        type = float,
        default = DEFAULT_VOLUME,
        help = 'Гучність звуку від 0.0 до 1.0. За замовчуванням: 0.5'
    )

    args = parser.parse_args()

    if not 0.0 <= args.volume <= 1.0:
        parser.error(f"Гучність повинна бути від 0.0 до 1.0!")

    args.ghost_speed = DIFFICULTY_SPEEDS[args.difficulty]

    return args