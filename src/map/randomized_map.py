import pygame
import random
from src.utils.constants import TILE_SIZE, GRID_HEIGHT, GRID_WIDTH, WIDTH, HEIGHT, BLUE, BLACK, FPS, MAP_OFFSET_Y

class RandomMap():
    """
    A procedurally generated Pac-Man maze.

    Builds a new symmetrical maze each time it is instantiated using a
    randomised recursive-division-style algorithm. The ghost pen is always
    placed at the centre, horizontal tunnels are carved at mid-height, and
    the left half is mirrored to the right for visual balance.

    Attributes:
        level (list[list[int]]): 2-D tile grid where 1 = wall, 0 = walkable,
            and 2 = ghost pen entrance marker.
        walls (list[pygame.Rect]): Pixel-space rects for every wall tile,
            used for collision detection and rendering.
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
        Generate the maze, build the wall rect list, and compute dimensions.

        Args:
            None

        Returns:
            None
        """
        self.level = self.generate_pacman_maze()
        self.walls = []
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
        during __init__ after the maze is generated.

        Args:
            None

        Returns:
            None
        """
        self.walls = []

        for y, row in enumerate(self.level):
            for x, tile in enumerate(row):
                if tile == 1:
                    self.walls.append(
                        pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    )


    def draw_map(self, screen: pygame.Surface):
        """
        Populate self.walls with a pygame.Rect for every wall tile in the grid.

        Iterates the full level grid and creates a TILE_SIZE × TILE_SIZE rect
        at the pixel position of each cell whose value is 1. Called once
        during __init__ after the maze is generated.

        Args:
            None

        Returns:
            None
        """
        for wall in self.walls:
            shifted = wall.move(0, MAP_OFFSET_Y)
            pygame.draw.rect(screen, BLUE, shifted, 2)


    def generate_pacman_maze(self) -> list[list[int]]: 
        """
        Procedurally build and return a symmetrical Pac-Man maze grid.

        Generation steps:
            1. Fill the grid with open tiles and place a solid border.
            2. Reserve a protected ghost-house zone around the centre to
               prevent random walls from encroaching on the pen.
            3. Carve the ghost pen as a hollow 5×5 box with a top entrance
               (tile value 2) and a cleared approach tile above it.
            4. Scatter internal walls on even-coordinate cells outside the
               ghost zone, randomly extending each wall one tile in a
               cardinal direction.
            5. Mirror the left half of the grid onto the right half for
               bilateral symmetry, skipping ghost-zone tiles.
            6. Carve two-tile-wide horizontal tunnels through both side
               borders at mid-height.

        Args:
            None

        Returns:
            list[list[int]]: Completed GRID_HEIGHT × GRID_WIDTH tile grid
                where 1 = wall, 0 = walkable, and 2 = ghost pen entrance.
        """
        level = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            level[y][0] = level[y][GRID_WIDTH-1] = 1
        for x in range(GRID_WIDTH):
            level[0][x] = level[GRID_HEIGHT-1][x] = 1

        cx, cy = GRID_WIDTH // 2, GRID_HEIGHT // 2

        ghost_house_zone = []
        for y in range(cy - 3, cy + 4):
            for x in range(cx - 4, cx + 5):
                ghost_house_zone.append((x, y))

        for y in range(cy - 2, cy + 3):
            for x in range(cx - 2, cx + 3):
                if x == cx-2 or x == cx+2 or y == cy-2 or y == cy+2:
                    level[y][x] = 1
                else:
                    level[y][x] = 0

        level[cy - 2][cx] = 2
        level[cy - 3][cx] = 0

        for y in range(2, GRID_HEIGHT - 2, 2):
            for x in range(2, GRID_WIDTH - 2, 2):
                if (x, y) in ghost_house_zone:
                    continue
                
                level[y][x] = 1
                if random.random() > 0.4:
                    side = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    nx, ny = x + side[0], y + side[1]
                    if (nx, ny) not in ghost_house_zone and 1 < nx < GRID_WIDTH-2 and 1 < ny < GRID_HEIGHT-2:
                        level[ny][nx] = 1

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH // 2):
                mirror_x = GRID_WIDTH - 1 - x
                if (mirror_x, y) not in ghost_house_zone:
                    level[y][mirror_x] = level[y][x]

        tunnel_y = GRID_HEIGHT // 2
        level[tunnel_y][0] = level[tunnel_y][1] = 0
        level[tunnel_y][GRID_WIDTH-1] = level[tunnel_y][GRID_WIDTH-2] = 0

        return level