import pytest
import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
from src.game_objects.object_manager import ObjectManager
from unittest.mock import patch


@pytest.mark.movement
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

@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=True)
def test_wall_collision(mock_collision, test_pacman):
    test_pacman.direction = pygame.Vector2(1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    old_x = TILE_SIZE 
    old_y = TILE_SIZE

    test_pacman.move()

    assert test_pacman.pos.x == old_x
    assert test_pacman.pos.y == old_y

@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=False)
def test_tunnel_left(mock_collision, test_pacman):
    test_pacman.rect.right = -1
    test_pacman.direction = pygame.Vector2(-1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == WIDTH + test_pacman.direction.x * test_pacman.speed

@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=False)
def test_tunnel_right(mock_collision, test_pacman):
    test_pacman.rect.left = WIDTH + 1
    test_pacman.direction = pygame.Vector2(1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == -test_pacman.rect.width + test_pacman.direction.x * test_pacman.speed

@pytest.mark.movement
@patch.object(ObjectManager, 'get_valid_tiles')
def test_collect_pellet(mock_get_valid_tiles, test_pacman, test_map):
    mock_get_valid_tiles.return_value = [(1, 1)]

    objects = ObjectManager(test_map)
    objects.spawn_pellets()

    test_pacman.rect.topleft = (1 * TILE_SIZE, 1 * TILE_SIZE)

    objects.update_objects(test_pacman)

    assert test_pacman.score == 10
    assert objects.pellets[0].eaten == True
