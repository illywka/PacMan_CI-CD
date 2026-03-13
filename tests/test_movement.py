import pytest
import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
from src.game_objects.object_manager import ObjectManager
from unittest.mock import patch

# --------------------Anastasiia-------------------


@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=False)
@pytest.mark.parametrize("direction, expected_x, expected_y", [
    ((0, -1), TILE_SIZE, TILE_SIZE - PACMAN_SPEED),
    ((0, 1), TILE_SIZE, TILE_SIZE + PACMAN_SPEED),
    ((-1, 0), TILE_SIZE - PACMAN_SPEED, TILE_SIZE),
    ((1, 0), TILE_SIZE + PACMAN_SPEED, TILE_SIZE)
])
def test_movement_directions(
        mock_collision, test_pacman, direction,
        expected_x, expected_y):
    '''
    Docstring for test_movement_directions

    Tests if Pacman moves correctly in all four directions
    when there are no collisions.

    :param mock_collision: Mocks collision check to always return False
    :param test_pacman: Test "Fake" Pacman
    :param direction: Tuple representing movement vector
    :param expected_x: Expected X coordinate after move
    :param expected_y: Expected Y coordinate after move
    '''
    test_pacman.direction = pygame.Vector2(direction)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == expected_x
    assert test_pacman.pos.y == expected_y


@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=True)
def test_wall_collision(mock_collision, test_pacman):
    '''
    Docstring for test_wall_collision

    Tests if Pacman stops moving when colliding with a wall.

    :param mock_collision: Mocks collision check to always return True
    :param test_pacman: Test "Fake" Pacman
    '''
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
    '''
    Docstring for test_tunnel_left

    Tests if Pacman teleports to the right side of the screen
    after entering the left tunnel.

    :param mock_collision: Mocks collision check
    :param test_pacman: Test "Fake" Pacman
    '''
    test_pacman.rect.right = -1
    test_pacman.direction = pygame.Vector2(-1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == (
        WIDTH + test_pacman.direction.x * test_pacman.speed
    )


@pytest.mark.movement
@patch('src.entities.entity.check_collision', return_value=False)
def test_tunnel_right(mock_collision, test_pacman):
    '''
    Docstring for test_tunnel_right

    Tests if Pacman teleports to the left side of the screen
    after entering the right tunnel.

    :param mock_collision: Mocks collision check
    :param test_pacman: Test "Fake" Pacman
    '''
    test_pacman.rect.left = WIDTH + 1
    test_pacman.direction = pygame.Vector2(1, 0)
    test_pacman.next_direction = pygame.Vector2(0, 0)

    test_pacman.move()

    assert test_pacman.pos.x == (
        -test_pacman.rect.width + test_pacman.direction.x * test_pacman.speed
    )


@pytest.mark.movement
@patch.object(ObjectManager, 'get_valid_tiles')
def test_collect_pellet(mock_get_valid_tiles, test_pacman, test_map):
    '''
    Docstring for test_collect_pellet

    Tests if Pacman successfully collects a pellet,
    increasing the score and marking the pellet as eaten.

    :param mock_get_valid_tiles: Mocks valid tiles for pellet spawning
    :param test_pacman: Test "Fake" Pacman
    :param test_map: Test "Fake" Map
    '''
    mock_get_valid_tiles.return_value = [(1, 1)]

    objects = ObjectManager(test_map)
    objects.spawn_pellets()

    test_pacman.rect.topleft = (1 * TILE_SIZE, 1 * TILE_SIZE)

    objects.update_objects(test_pacman)

    assert test_pacman.score == 10
    assert objects.pellets[0].eaten
