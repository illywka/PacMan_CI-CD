import pygame
import pytest
from unittest.mock import patch

from src.utils.constants import TILE_SIZE
from src.core.game import Game  
from src.game_objects.object_manager import ObjectManager

#-----------------------Illia-----------------------
def test_pacman_lose_lives_games_ends(test_pacman, test_ghost):
    '''
    Docstring for test_pacman_lose_lives_games_ends

    Tests if games ends when Pacman in collide with Ghost and Pacman has 1 life left.
    
    :param test_pacman: Test "Fake" Pacman
    :param test_ghost: Test "Fake" Ghost
    '''
    game = Game()

    game.game_state = "game"
    
    test_pacman.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)
    test_ghost.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)
    
    test_pacman.lives = 1
    test_pacman.shielded = False
    game.player = test_pacman

    test_ghost.is_scared = False
    test_ghost.is_dead = False
    game.ghosts_group = [test_ghost]

    game._handle_collisions()
    
    assert test_pacman.lives == 0
    assert game.game_state == "lose"

@patch('src.game_objects.object_manager.time.time')
@patch.object(ObjectManager, 'get_valid_tiles')
def test_pacman_use_boost(mock_get_valid_tiles, mock_time, test_pacman, test_map):
    '''
    Docstring for test_end_boost_time

    Tests if PacMan uses boost

    :param mock_get_valid_tiles: Mocks valid tiles
    :param mock_time: Mocks time
    :param test_pacman: Test "Fake" Pacman
    :param test_map: Test "Fake" Map
    '''

    mock_get_valid_tiles.return_value = [(1,1)]
    mock_time.return_value = 100

    test_pacman.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)

    objects = ObjectManager(test_map)
    objects.spawn_boost()

    objects.update_objects(test_pacman)

    assert test_pacman.active_boosts or test_pacman.score == 1000

def test_pacman_eat_ghost(test_pacman, test_ghost):
    '''
    Docstring for test_pacman_eat_ghost

    Tests if Pacman can eat scared ghsot

    :param test_pacman: Test "Fake" Pacman
    :param test_ghost: Test "Fake" Ghost
    '''
    game = Game()
    
    test_pacman.shielded = True
    test_pacman.active_boosts["shield"] = 10

    test_pacman.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)
    test_ghost.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)
    test_ghost.is_dead = False

    game.player = test_pacman
    game.ghosts_group=[test_ghost]
    game._update()

    game._handle_collisions()

    assert test_ghost.is_dead == True

@patch.object(ObjectManager, 'get_valid_tiles')
def test_game_won(mock_get_valid_tiles, test_pacman, test_map):
    mock_get_valid_tiles.return_value = [(1,1)]
    objects = ObjectManager(test_map)
    game = Game()

    game.game_state = "game"

    objects.spawn_pellets()

    test_pacman.rect.topleft = (1*TILE_SIZE, 1*TILE_SIZE)

    game.objects = objects
    game.objects.update_objects(test_pacman)
    
    game._check_win_condition()

    assert game.game_state == "win"

    
#-------------------------------------------------
#--------------------Anastasiia-------------------