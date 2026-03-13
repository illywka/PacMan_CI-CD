import pytest
import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED
from unittest.mock import MagicMock, patch


#@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=False)
@pytest.mark.parametrize("direction, expected_x, expected_y", [
    ((0, -1), TILE_SIZE, TILE_SIZE - PACMAN_SPEED), #вгору
    ((0, 1), TILE_SIZE, TILE_SIZE + PACMAN_SPEED), #вниз
    ((-1, 0), TILE_SIZE - PACMAN_SPEED, TILE_SIZE), #вліво 
    ((1, 0), TILE_SIZE + PACMAN_SPEED, TILE_SIZE)  #вправо
])
def test_movement_directions(mock_collision, test_pacman, direction, expected_x, expected_y):
    test_pacman.direction = pygame.Vector2(direction)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == expected_x
    assert test_pacman.pos.y == expected_y


@patch('src.entities.entity.check_collision', return_value=True)
def test_wall_collision(mock_collision, test_pacman):
    test_pacman.direction = pygame.Vector2(1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    old_x = TILE_SIZE 
    old_y = TILE_SIZE

    test_pacman.move()

    assert test_pacman.pos.x == old_x
    assert test_pacman.pos.y == old_y
