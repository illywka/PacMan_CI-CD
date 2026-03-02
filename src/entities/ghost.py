import pygame

from collections import deque
from abc import ABC, abstractmethod
from src.utils.constants import TILE_SIZE, GHOST_SPEED, WIDTH, FPS
import src.entities.entity as entity

import random

class Ghost(pygame.sprite.Sprite, ABC):
    """
    Abstract base class for all ghost enemies.

    Provides shared pathfinding (BFS), movement, sprite animation, speed
    management, and spawn logic. Each concrete subclass defines its own
    targeting strategy via get_target() and its sprite sheet via the
    class-level ``sprite`` attribute.

    Class Attributes:
        directions (list[tuple[int, int]]): The four cardinal movement
            offsets (row, col) used by BFS and movement logic.

    Attributes:
        rect (pygame.Rect): Bounding box used for rendering and collision.
        base_speed (float): Reference speed set by difficulty; never
            modified after init so change_speed() can scale from it.
        speed (float): Current per-frame pixel speed, scaled by state.
        direction (pygame.Vector2): Unit vector of current movement.
        next_direction (pygame.Vector2): Queued direction to apply at the
            next tile centre.
        clock (pygame.time.Clock): Local clock (reserved for subclass use).
        game_map (Map | RandomMap): Reference to the active level map.
        empty_tiles (list[tuple[int, int]]): Walkable tiles in the central
            pen region, used for spawn and house-exit logic.
        random_empty_tile (tuple[int, int]): The tile chosen as this
            ghost's spawn point.
        start_pos (pygame.Vector2): Pixel coordinate of the spawn tile.
        pos (pygame.Vector2): Current sub-pixel position used for movement.
        pacman (Pacman): Reference to the player sprite.
        path (list): Current BFS direction list being followed.
        sprite_start (tuple[int, int]): Top-left offset into the sprite sheet
            for the current animation frame.
        sprite_width (tuple[int, int]): Width/height of a single sprite frame.
        sprite_dead (pygame.Surface): Sprite sheet used when the ghost is
            dead or scared.
        is_scared (bool): True while the player's shield boost is active.
        is_dead (bool): True after the ghost has been killed by a shield
            collision; ghost returns to pen before reviving.
        spawn_time (int): pygame.time.get_ticks() value recorded at spawn,
            used to time the house-exit delay.
    """
    directions = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    def __init__(self, game_map, pacman):
        """
        Initialise shared ghost state, pick a random spawn tile, and load
        the dead/scared sprite sheet.

        Args:
            game_map (Map | RandomMap): The active level map providing the
                tile grid and wall rects.
            pacman (Pacman): The player sprite, used by targeting methods.

        Returns:
            None
        """
        super().__init__()

        self.rect = pygame.Rect(9*TILE_SIZE, 12*TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.base_speed = GHOST_SPEED
        self.speed = self.base_speed

        self.direction = pygame.Vector2(0, -1)
        self.next_direction = pygame.Vector2(0, 0)
        self.clock = pygame.time.Clock()
        self.game_map = game_map

        self.empty_tiles = self.find_empty_center_tiles()
        self.random_empty_tile = random.choice(self.empty_tiles)
        self.start_pos = pygame.Vector2(self.random_empty_tile[1]*TILE_SIZE, self.random_empty_tile[0]*TILE_SIZE)
        self.pos = self.start_pos.copy()

        self.x = self.start_pos.copy()[1]
        self.y = self.start_pos.copy()[0]

        self.pacman = pacman

        self.path = [[0, 0]]
        self.sprite_start = (0, 0)
        self.sprite_width = (16, 16)

        self.sprite_dead = pygame.image.load(f'src/assets/ghosts/killed_ghost/killed_ghost.png')

        self.is_scared = False
        self.is_dead = False

        self.spawn_time = pygame.time.get_ticks()
        
    @property
    @abstractmethod
    def image(self) -> pygame.Surface:
        """
        Return the current animation frame for this ghost.

        Subclasses must implement this property and typically delegate to
        change_sprite().

        Returns:
            pygame.Surface: The surface to blit each frame.
        """
        pass
    
    @abstractmethod
    def get_target(self) -> tuple[int, int]:
        """
        Return the (row, col) tile this ghost is currently chasing.

        Each subclass implements a distinct targeting strategy:
            - Pinky: predicts Pac-Man's position 4 tiles ahead.
            - Inky:  predicts using reversed direction priority.
            - Sue:   targets Pac-Man's current tile directly.
            - Clyde: wanders to random non-walkable tiles.

        Returns:
            tuple[int, int]: The (row, col) grid coordinate to pathfind toward.
        """
        pass

    def pathfind(self):
        """
        Compute the next BFS path step and advance the ghost by one frame.

        Called every update cycle. When the ghost is centred on a tile the
        target is recalculated and a fresh BFS path is generated. The first
        direction in that path is queued as next_direction, then move() is
        called to apply movement.

        Targeting priority (evaluated when centred on a tile):
            1. If time_out seconds have elapsed and the ghost is still in
               the pen, call open_tile_for_ghost() to exit.
            2. If still in the pen (but timeout not reached), wander among
               pen tiles.
            3. If is_dead, pathfind back to start_pos.
            4. Otherwise, delegate to get_target().

        Args:
            None

        Returns:
            None
        """
        if entity.is_centered(self):
            seconds = (pygame.time.get_ticks() - self.spawn_time) / 1000
            
            if seconds >= self.time_out and self.get_current_tile() in self.empty_tiles:
                self.is_dead = False
                target_tile = self.open_tile_for_ghost()
                
            elif self.get_current_tile() in self.empty_tiles:
                available_tiles = self.empty_tiles.copy()
                if self.get_current_tile() in available_tiles:
                    available_tiles.remove(self.get_current_tile())
                if available_tiles:
                    target_tile = random.choice(available_tiles)
                else:
                    target_tile = self.get_current_tile()
            elif self.is_dead:
                target_tile = (round(self.start_pos[1] / TILE_SIZE), round(self.start_pos[0] / TILE_SIZE))
            else:
                target_tile = self.get_target()

            self.path = self.bfs(self.game_map.level, self.get_current_tile(), target_tile)
            
            if self.path and len(self.path) > 0:
                self.next_direction = pygame.Vector2(self.path[0])

        self.move()

    def find_empty_center_tiles(self) -> list[tuple[int,int]]:
        """
        BFS-flood from the map centre outward to collect all connected
        walkable (value 0) tiles in the ghost pen region.

        Used to determine valid spawn positions and to detect when a ghost
        is still inside the pen.

        Args:
            None

        Returns:
            list[tuple[int, int]]: Sorted list of (row, col) walkable tile
                coordinates reachable from the map's centre cell.
        """
        rows = self.game_map.height
        cols = self.game_map.width

        start_y, start_x = rows // 2, cols // 2

        visited = set()
        queue = deque([(start_y, start_x)])
        inner_zeros = []
        
        visited.add((start_y, start_x))
        
        while queue:
            y, x = queue.popleft()
            inner_zeros.append((y, x))
            
            for dy, dx in self.directions:
                next_y, next_x = y + dy, x + dx
                
                if 0 <= next_y < rows and 0 <= next_x < cols:
                    if self.game_map.level[next_y][next_x] == 0 and (next_y, next_x) not in visited:
                        visited.add((next_y, next_x))
                        queue.append((next_y, next_x))
                        
        return sorted(inner_zeros)

    def open_tile_for_ghost(self) -> tuple[int,int]:
        """
        Return the exit tile just above the pen entrance so a ghost can
        leave the house when its timeout has elapsed.

        Targets two rows above the second pen tile, placing the ghost at
        the threshold between the pen and the open maze.

        Args:
            None

        Returns:
            tuple[int, int]: The (row, col) tile coordinate for the pen exit.
        """
        open_tile = self.empty_tiles[1]

        return (open_tile[0]-2, open_tile[1])

    def change_sprite(self) -> pygame.Surface:
        """
        Select and return the correct animation frame based on the ghost's
        current state and direction.

        Alternates between two frames at a rate derived from FPS to create
        a simple two-frame walk cycle. State priority: scared > dead > normal.
        Normal state selects the row in the sprite sheet that corresponds
        to the current movement direction.

        Args:
            None

        Returns:
            pygame.Surface: A 16×16 subsurface cropped from either the
                ghost's own sprite sheet (normal) or sprite_dead
                (scared/dead).
        """
        tick = (pygame.time.get_ticks()//(FPS*4))%2

        if self.is_scared:
            self.sprite_start = (0, TILE_SIZE*tick)
        elif self.is_dead:
            self.sprite_start = (16, TILE_SIZE*tick)
        else:
            if self.direction == pygame.Vector2(1, 0):
                self.sprite_start = (0, TILE_SIZE*tick)
            elif self.direction == pygame.Vector2(-1, 0):
                self.sprite_start = (16, TILE_SIZE*tick)
            elif self.direction == pygame.Vector2(0, -1):
                self.sprite_start = (32, TILE_SIZE*tick)
            elif self.direction == pygame.Vector2(0, 1):
                self.sprite_start = (48, TILE_SIZE*tick)

            return self.sprite.subsurface((self.sprite_start, self.sprite_width))
        
        return self.sprite_dead.subsurface((self.sprite_start, self.sprite_width))

    def bfs(self, matrix: list[list[int]], start: tuple[int, int], goal: tuple[int, int], avoid_pacman: bool=False) -> list|None:
        """
        Run a breadth-first search on the tile grid from start to goal.

        Treats cells with value 1 as walls. The grid wraps horizontally and
        vertically via modulo arithmetic, matching the tunnel behaviour of
        the maze. Optionally skips Pac-Man's current tile to allow
        avoidance behaviour.

        Args:
            matrix (list[list[int]]): 2-D tile grid where 1 = wall,
                0 = walkable.
            start (tuple[int, int]): Starting (row, col) tile.
            goal (tuple[int, int]): Target (row, col) tile.
            avoid_pacman (bool): If True, the cell currently occupied by
                Pac-Man is treated as impassable. Defaults to False.

        Returns:
            list | None: Ordered list of (dx, dy) direction tuples leading
                from start to goal, or None if no path exists.
        """
        rows, cols = len(matrix), len(matrix[0])
        queue = deque([start])
        visited = {start: None}
        
        pacman_grid_pos = None
        if avoid_pacman:
            pacman_grid_pos = (round(self.pacman.pos.y / TILE_SIZE), round(self.pacman.pos.x / TILE_SIZE))

        while queue:
            current = queue.popleft()

            if current == goal:
                return self.reconstruct_path(visited, goal)
                
            for dr, dc in self.directions:
                r = (current[0] + dr) % rows
                c = (current[1] + dc) % cols
                neighbor = (r, c)
                
                if matrix[r][c] != 1 and neighbor not in visited:
                    if avoid_pacman and neighbor == pacman_grid_pos:
                        continue
                    
                    visited[neighbor] = current
                    queue.append(neighbor)
        
        return None

    def reconstruct_path(self, visited: dict, goal: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Convert the BFS visited-parent map into an ordered list of
        (dx, dy) movement directions.

        Walks the parent chain from goal back to the start, then reverses
        the list and converts consecutive tile pairs into direction vectors.
        Wrap-around edges (where the absolute tile delta exceeds 1) are
        corrected so the direction always has magnitude 1.

        Args:
            visited (dict): Mapping of tile -> parent tile produced by bfs().
            goal (tuple[int, int]): The destination tile used as the chain
                starting point.

        Returns:
            list[tuple[int, int]]: Chronologically ordered list of (dx, dy)
                unit direction tuples from the ghost's current tile to goal.
        """
        self.path = []
        curr = goal
        while curr is not None:
            self.path.append(curr)
            curr = visited[curr]
        
        dir_list = []

        for i in range(len(self.path)-1):
            target = self.path[i]
            source = self.path[i+1]
            
            dy = target[0] - source[0]
            dx = target[1] - source[1]

            if dy > 1:  dy = -1 
            elif dy < -1: dy = 1 
            
            if dx > 1:  dx = -1 
            elif dx < -1: dx = 1 

            dir_list.append((dx, dy))
            
        return dir_list[::-1]

    def future_pos(self, pos: pygame.Vector2, dir: pygame.Vector2) -> tuple[int, int]:
        """
        Convert a pixel position and direction vector into the tile
        coordinate one step ahead.

        Args:
            pos (pygame.Vector2): Current pixel position (x, y).
            dir (pygame.Vector2): Direction vector whose x and y components
                are used as column and row offsets respectively.

        Returns:
            tuple[int, int]: The (row, col) tile one step ahead of pos
                in the given direction.
        """
        return int(pos[0])//TILE_SIZE + int(dir[1]), int(pos[1])//TILE_SIZE + int(dir[0])
    
    def predict_future_position(self, directions: list[tuple[int, int]]) -> tuple[int, int]:
        """
        Predict where Pac-Man will be 4 steps in the future by simulating
        movement along valid tiles.

        At each step the method tries each direction in the supplied order,
        skipping moves that would enter a wall or reverse the current
        direction, then advances Pac-Man's simulated position by one tile.

        Args:
            directions (list[tuple[int, int]]): Priority-ordered list of
                (row_offset, col_offset) direction tuples to try at each
                step. Pinky passes the default order; Inky passes it reversed.

        Returns:
            tuple[int, int]: The predicted (row, col) tile after 4 steps.
        """
        dir = self.pacman.direction
        pos = self.pacman.pos
        for _ in range(1, 5):
            curr_dir = dir
            for i in range(0, 4):
                dir = pygame.Vector2(directions[i])
                y, x = self.future_pos(pos, dir)
                
                if y > len(self.game_map.level[0])-1:
                    y = len(self.game_map.level[0])-1
                if y < 0:
                    y = 0
        
                if self.game_map.level[x][y] != 0 or curr_dir == -dir:
                    continue
                else:
                    break
            predict_pos = self.future_pos(pos, dir)
            pos = pygame.Vector2(predict_pos[0]*TILE_SIZE, predict_pos[1]*TILE_SIZE)
        return predict_pos[1], predict_pos[0]

    def change_speed(self):
        """
        Adjust self.speed based on the ghost's current state.

        Dead ghosts move at 3× base speed to return to the pen quickly.
        Scared ghosts move at 0.5× base speed. Otherwise speed equals
        base_speed.

        Args:
            None

        Returns:
            None
        """
        if self.is_dead:
            self.speed = self.base_speed * 3
        elif self.is_scared:
            self.speed = self.base_speed * 0.5
        else:
            self.speed = self.base_speed

    def get_current_tile(self) -> tuple[int, int]:
        """
        Return the (row, col) tile that the ghost's position maps to.

        Rounds the pixel position to the nearest tile using TILE_SIZE,
        with row derived from the y axis and column from the x axis.

        Args:
            None

        Returns:
            tuple[int, int]: The ghost's current (row, col) grid tile.
        """
        return (round(self.pos[1] / TILE_SIZE), round(self.pos[0] / TILE_SIZE))
    
    def move(self):
        """
        Apply queued direction changes and advance the ghost by one frame.

        Direction change: when next_direction differs from the current
        direction, the ghost snaps to the nearest tile centre and attempts
        the turn. If the new direction is blocked the original position is
        restored and the ghost continues straight.

        Tunnel wrapping: if the ghost exits the left or right edge of the
        screen it is teleported to the opposite side.

        Movement: if the current direction is unobstructed, pos is advanced
        by speed pixels. If blocked, pos snaps to the tile centre to prevent
        wall clipping.

        Args:
            None

        Returns:
            None
        """
        if self.next_direction != pygame.Vector2(0, 0) and self.direction != self.next_direction:
            old_pos = self.pos.copy()
            old_rect_topleft = self.rect.topleft

            current_tile_x = (self.rect.centerx // TILE_SIZE) * TILE_SIZE
            current_tile_y = (self.rect.centery // TILE_SIZE) * TILE_SIZE

            self.pos.x = current_tile_x
            self.pos.y = current_tile_y
            self.rect.topleft = (self.pos.x, self.pos.y)

            if not entity.check_collision(self, self.next_direction):
                self.direction = self.next_direction
            else:
                self.pos = old_pos
                self.rect.topleft = old_rect_topleft

        if self.rect.right < 0:
            self.pos.x = WIDTH
            self.rect.x = WIDTH
        elif self.rect.left > WIDTH:
            self.pos.x = -self.rect.width
            self.rect.x = -self.rect.width

        if not entity.check_collision(self, self.direction):
            self.pos += self.direction * self.speed
        else:
            self.pos.x = (self.rect.centerx // TILE_SIZE) * TILE_SIZE
            self.pos.y = (self.rect.centery // TILE_SIZE) * TILE_SIZE
        
        self.rect.topleft = round(self.pos.x), round(self.pos.y)


#Pinky, Inky, Sue, Clyde
class Pinky(Ghost):
    """
    Pink ghost — targets 4 tiles ahead of Pac-Man's current direction.

    Leaves the pen after 2 seconds. Uses the default direction priority
    order for future-position prediction, so it tends to cut Pac-Man off
    from the front.

    Class Attributes:
        sprite (pygame.Surface): Sprite sheet for Pinky's normal animations.
    """
    sprite = pygame.image.load(f'src/assets/ghosts/pink_ghost/pink_ghost.png')
    def __init__(self, game_map, pacman):
        """
        Args:
            game_map (Map | RandomMap): The active level map.
            pacman (Pacman): The player sprite.

        Returns:
            None
        """
        self.time_out = 2
        super().__init__(game_map, pacman)
    
    @property
    def image(self) -> pygame.Surface:
        """
        Returns:
            pygame.Surface: The current animation frame via change_sprite().
        """
        return self.change_sprite()

    def get_target(self) -> tuple[int, int]:
        """
        Predict Pac-Man's position 4 steps ahead using the default
        direction priority.

        Returns:
            tuple[int, int]: Predicted (row, col) target tile.
        """
        return self.predict_future_position(self.directions)

    def update(self):
        """
        Update speed and advance pathfinding/movement for this frame.

        Args:
            None

        Returns:
            None
        """
        self.change_speed()
        self.pathfind()

class Inky(Ghost):
    """
    Cyan ghost — targets 4 tiles ahead of Pac-Man using reversed direction
    priority, producing unpredictable flanking behaviour.

    Leaves the pen after 6 seconds.

    Class Attributes:
        sprite (pygame.Surface): Sprite sheet for Inky's normal animations.
    """
    sprite = pygame.image.load(f'src/assets/ghosts/cyan_ghost/cyan_ghost.png')
    def __init__(self, game_map, pacman):
        """
        Args:
            game_map (Map | RandomMap): The active level map.
            pacman (Pacman): The player sprite.

        Returns:
            None
        """
        self.time_out = 6
        super().__init__(game_map, pacman)
    
    @property
    def image(self) -> pygame.Surface:
        """
        Returns:
            pygame.Surface: The current animation frame via change_sprite().
        """
        return self.change_sprite()
    
    def get_target(self) -> tuple[int, int]:
        """
        Predict Pac-Man's position 4 steps ahead using the reversed
        direction priority list.

        Returns:
            tuple[int, int]: Predicted (row, col) target tile.
        """
        return self.predict_future_position(self.directions[::-1])

    def update(self):
        """
        Update speed and advance pathfinding/movement for this frame.

        Args:
            None

        Returns:
            None
        """
        self.change_speed()
        self.pathfind()

class Sue(Ghost):
    """
    Purple ghost — directly chases Pac-Man's current tile with no
    prediction, making her the simplest but most persistent pursuer.

    Leaves the pen after 8 seconds.

    Class Attributes:
        sprite (pygame.Surface): Sprite sheet for Sue's normal animations.
    """
    sprite = pygame.image.load(f'src/assets/ghosts/purple_ghost/purple_ghost.png')
    
    def __init__(self, game_map, pacman):
        """
        Args:
            game_map (Map | RandomMap): The active level map.
            pacman (Pacman): The player sprite.

        Returns:
            None
        """
        self.time_out = 8
        super().__init__(game_map, pacman)
    
    @property
    def image(self) -> pygame.Surface:
        """
        Returns:
            pygame.Surface: The current animation frame via change_sprite().
        """
        return self.change_sprite()

    def get_target(self) -> tuple[int, int]:
        """
        Return Pac-Man's current tile as the chase target.

        Returns:
            tuple[int, int]: Pac-Man's current (row, col) grid tile.
        """
        return (round(self.pacman.pos[1] / TILE_SIZE), round(self.pacman.pos[0] / TILE_SIZE))

    def update(self):
        """
        Update speed and advance pathfinding/movement for this frame.

        Args:
            None

        Returns:
            None
        """
        self.change_speed()
        self.pathfind()

class Clyde(Ghost):
    """
    Brown ghost — wanders toward random non-walkable tiles, creating
    erratic, hard-to-predict movement.

    When the current path is exhausted, a new random tile coordinate is
    chosen. If that tile happens to be walkable the ghost idles until the
    path runs out again.

    Leaves the pen after 4 seconds.

    Class Attributes:
        sprite (pygame.Surface): Sprite sheet for Clyde's normal animations.
    """
    sprite = pygame.image.load(f'src/assets/ghosts/brown_ghost/brown_ghost.png')
    def __init__(self, game_map, pacman):
        """
        Args:
            game_map (Map | RandomMap): The active level map.
            pacman (Pacman): The player sprite.

        Returns:
            None
        """
        self.time_out = 4
        super().__init__(game_map, pacman)

    @property
    def image(self) -> pygame.Surface:
        """
        Returns:
            pygame.Surface: The current animation frame via change_sprite().
        """
        return self.change_sprite()
    
    def get_target(self) -> tuple[int, int]|None:
        """
        Pick a random map tile as the next target when the current path is
        exhausted, provided the tile is not a walkable pen tile.

        A new random (row, col) coordinate is chosen only when self.path is
        empty or None. The target is only returned if it falls outside the
        pen's empty_tiles list, encouraging Clyde to roam wall-adjacent areas.

        Returns:
            tuple[int, int] | None: The (row, col) target tile, or None if
                the randomly chosen tile is inside the pen.
        """
        if self.path is None or not len(self.path) > 0:
            self.x = random.randint(1, len(self.game_map.level)-2)
            self.y = random.randint(0, len(self.game_map.level[0])-1)

        if (self.x, self.y) not in self.empty_tiles:
            return (self.x, self.y)

    def update(self):
        """
        Update speed and advance pathfinding/movement for this frame.

        Args:
            None

        Returns:
            None
        """
        self.change_speed()
        self.pathfind()