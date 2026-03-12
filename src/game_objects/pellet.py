import pygame
from src.utils.constants import TILE_SIZE, WHITE, MAP_OFFSET_Y


class Pellet:
    """
    A single collectible pellet drawn as a small filled circle.

    Pellets are placed on every valid walkable tile at level start.
    ObjectManager checks each pellet's rect for collision with the player
    and sets eaten to True on collection, awarding points and contributing
    toward the win condition when all pellets are eaten.

    Attributes:
        grid_x (int): Column index of the pellet's tile in the level grid.
        grid_y (int): Row index of the pellet's tile in the level grid.
        x (int): Pixel x coordinate of the pellet's centre.
        y (int): Pixel y coordinate of the pellet's centre.
        radius (int): Radius in pixels of the drawn circle and collision rect.
        rect (pygame.Rect): Bounding box centred on (x, y) used for collision
            detection by ObjectManager.
        eaten (bool): True once the player has collected this pellet; eaten
            pellets are neither drawn nor scored again.
    """
    def __init__(self, grid_x: int, grid_y: int):
        """
        Initialise the pellet at the centre of the given grid tile.

        Converts tile coordinates to pixel coordinates and builds a
        square collision rect whose side length equals the circle's diameter.

        Args:
            grid_x (int): Column index of the tile to place this pellet on.
            grid_y (int): Row index of the tile to place this pellet on.

        Returns:
            None
        """
        self.grid_x = grid_x
        self.grid_y = grid_y

        self.x = grid_x * TILE_SIZE + TILE_SIZE//2
        self.y = grid_y * TILE_SIZE + TILE_SIZE//2

        self.radius = 2
        self.rect = pygame.Rect(
            self.x - self.radius,
            self.y - self.radius,
            self.radius * 2,
            self.radius * 2
        )
        self.eaten = False

    def draw(self, screen: pygame.Surface):
        """
        Draw the pellet as a filled white circle if it has not been eaten.

        Applies MAP_OFFSET_Y to the y coordinate so the pellet renders
        in the play area below the HUD rather than at its raw grid position.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface.

        Returns:
            None
        """
        if not self.eaten:
            center_x = self.rect.centerx
            center_y = self.rect.centery + MAP_OFFSET_Y
            pygame.draw.circle(
                screen, WHITE, (center_x, center_y), self.radius)
