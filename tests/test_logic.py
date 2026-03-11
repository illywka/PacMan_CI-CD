import pygame
from src.utils.constants import TILE_SIZE

def test_pacman_dies_on_ghost_collision(test_pacman, test_ghost):
    """
    Тестування зіткнення Пакмена та одного Привида.
    
    Якщо Привид і Пакмен в одному місці - is_dead повинне бути True
    """
    
    test_pacman.rect.x = 1*TILE_SIZE
    test_ghost.rect.x = 1*TILE_SIZE
    test_pacman.rect.y = 1*TILE_SIZE
    test_ghost.rect.y = 1*TILE_SIZE
    
    is_dead = pygame.sprite.collide_rect(test_pacman, test_ghost)
    
    assert is_dead == True