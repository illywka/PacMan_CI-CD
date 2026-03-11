import pygame
from src.utils.constants import TILE_SIZE
from src.core.game import Game  

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

    test_ghost.is_scared = True
    test_ghost.is_dead = False
    game.ghosts_group = [test_ghost]

    game._handle_collisions()
    
    assert test_pacman.lives == 0
    assert game.game_state == "lose"

