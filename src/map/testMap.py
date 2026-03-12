import pygame
from src.utils.constants import TILE_SIZE, BLUE, MAP_OFFSET_Y


class Map():
    """
    A fixed, hand-authored Pac-Man maze.

    Provides the same level layout every game, as opposed to RandomMap which
    generates a new maze procedurally. The grid is a 25×19 tile layout with
    a central ghost pen, side tunnels on rows 9–15, and bilateral symmetry.

    Tile values:
        0 — walkable open floor
        1 — wall
        2 — ghost pen entrance marker

    Attributes:
        walls (list[pygame.Rect]): Pixel-space rects for every wall tile,
            used for collision detection and rendering.
        level (list[list[int]]): 2-D tile grid defining the fixed map layout.
        height (int): Number of tile rows in the grid.
        width (int): Number of tile columns in the grid.
        ghost_zone_size (int): Side length of the square ghost pen (3 tiles).
        ghost_start_x (int): Column index of the top-left corner of the
            ghost pen, centred horizontally.
        ghost_start_y (int): Row index of the top-left corner of the
            ghost pen, centred vertically.
    """
    def __init__(self):
        """
        Initialise the fixed map, build wall rects, and compute dimensions.

        Args:
            None

        Returns:
            None
        """
        self.walls = []
        self.level = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1, 0, 1, 1, 2, 1, 1, 0, 1, 0, 1, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1],
            [0, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0],
            [0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0],
            [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        self.create_walls()

        self.height = len(self.level)
        self.width = len(self.level[0])

        self.ghost_zone_size = 3
        self.ghost_start_x = self.width // 2 - 1
        self.ghost_start_y = self.height // 2 - 1

    def create_walls(self):
        """
        Populate self.walls with a pygame.Rect for every wall tile in the grid.

        Iterates the full level grid and creates a TILE_SIZE × TILE_SIZE rect
        at the pixel position of each cell whose value is 1. Called once
        during __init__ after the level data is defined.

        Args:
            None

        Returns:
            None
        """
        self.walls = []

        for y, row in enumerate(self.level):
            for x, tile in enumerate(row):
                if tile == 1:
                    self.walls.append(pygame.Rect(
                        x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def draw_map(self, screen: pygame.Surface):
        """
        Draw all wall rects as hollow blue rectangles onto the screen.

        Each wall rect is shifted down by MAP_OFFSET_Y so the maze renders
        below the HUD. Walls are drawn as outlines (border width 2) rather
        than filled to match the classic Pac-Man aesthetic.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface.

        Returns:
            None
        """
        for wall in self.walls:
            shifted = wall.move(0, MAP_OFFSET_Y)
            pygame.draw.rect(screen, BLUE, shifted, 2)
