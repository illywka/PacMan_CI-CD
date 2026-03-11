import pytest
import pygame
import os

from unittest.mock import MagicMock

os.environ["SDL_VIDEODRIVER"] = "dummy" # Для створення видимості ніби вікно створилось
os.environ["SDL_AUDIODRIVER"] = "dummy" # Для створення видимості ніби аудіо створилось

from src.utils.constants import TILE_SIZE
from src.entities.pacman import Pacman
from src.entities.ghost import Pinky

mock_map = MagicMock()
    
mock_map.width = 4*TILE_SIZE
mock_map.height = 4*TILE_SIZE


@pytest.fixture(autouse=True)
def init_dummy_pygame():
    """
    Автоматично ініціалізує фейковий Pygame перед кожним тестом.
    Це необхідно, щоб функції на кшталт .convert_alpha() працювали без помилок.
    """
    pygame.init()
    pygame.display.set_mode((1, 1))
    yield
    pygame.quit()


@pytest.fixture
def test_pacman():
    mock_sound_manager = MagicMock()

    global player
    player = Pacman(TILE_SIZE, TILE_SIZE, game_map=mock_map, sound_manager=mock_sound_manager)

    return player

@pytest.fixture
def test_ghost():
    return Pinky(mock_map, player)