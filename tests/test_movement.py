import pytest
import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED
from unittest.mock import MagicMock, patch


#@pytest.mark.movement
@pytest.mark.parametrize("direction, expected_x, expected_y", [
    ((0, -1), TILE_SIZE, TILE_SIZE - PACMAN_SPEED), #вгору
    ((0, 1), TILE_SIZE, TILE_SIZE + PACMAN_SPEED), #вниз
    ((-1, 0), TILE_SIZE - PACMAN_SPEED, TILE_SIZE), #вліво 
    ((1, 0), TILE_SIZE + PACMAN_SPEED, TILE_SIZE)  #вправо
])
def test_movement_directions(test_pacman, direction, expected_x, expected_y):
    with patch('src.entities.entity.check_collision', return_value=False):
        test_pacman.direction = pygame.Vector2(direction)
        test_pacman.next_direction = pygame.Vector2(0, 0)

        test_pacman.move()

        assert test_pacman.pos.x == expected_x
        assert test_pacman.pos.y == expected_y
    