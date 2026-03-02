import random
import time
import pygame
from collections import deque
from src.game_objects.pellet import Pellet
from src.game_objects.boost import CakeBoost, StrawberryBoost, WatermelonBoost
from src.utils.constants import TILE_SIZE

class ObjectManager:
    """
    Manages all collectible objects on the map: pellets and rotating boosts.

    Responsible for spawning pellets across every valid walkable tile,
    periodically replacing the active boost with a newly chosen one, detecting
    collection collisions with the player, and drawing all live objects.

    Attributes:
        map (Map | RandomMap): Reference to the active level map.
        pellets (list[Pellet]): All pellet instances for the current level;
            each tracks its own eaten state.
        boosts (list): Reserved for future multi-boost support (unused).
        current_boost (Boost | None): The single active boost item, or None
            if no boost is currently on the map.
        last_boost_time (float): time.time() timestamp of the last boost
            rotation, used to measure the boost_interval.
        boost_interval (int): Seconds between boost rotations.
    """
    def __init__(self, game_map):
        """
        Initialise the manager with an empty object state.

        Args:
            game_map (Map | RandomMap): The active level map providing the
                tile grid, dimensions, and ghost zone coordinates.

        Returns:
            None
        """
        self.map = game_map
        self.pellets = []
        self.boosts = []
        self.current_boost = None
        self.last_boost_time = 0
        self.boost_interval = 10
        self.last_pellet_sfx_time = 0
        self.pellet_sfx_cooldown = 0.2

    def is_walkable(self, x: int , y: int) -> bool:
        """
        Return whether the tile at (x, y) is an open (non-wall) cell.

        Args:
            x (int): Column index in the tile grid.
            y (int): Row index in the tile grid.

        Returns:
            bool: True if the tile value is 0 (walkable), False otherwise.
        """
        return self.map.level[y][x] == 0

    def is_ghost_zone(self, x: int, y: int) -> bool:
        """
        Return whether the tile at (x, y) falls inside the ghost pen.

        The ghost pen is defined as a 3×3 block starting at
        (ghost_start_x, ghost_start_y) on the map. Pellets and boosts are
        never placed here.

        Args:
            x (int): Column index in the tile grid.
            y (int): Row index in the tile grid.

        Returns:
            bool: True if the tile is within the ghost spawn region.
        """
        return(self.map.ghost_start_x <= x < self.map.ghost_start_x + 3 and 
               self.map.ghost_start_y <= y < self.map.ghost_start_y + 3)

    def find_reachable_tiles(self, start_x: int, start_y: int) -> set[tuple[int, int]]:
        """
        BFS-flood from (start_x, start_y) and return all connected walkable tiles.

        Used to exclude isolated walkable pockets that Pac-Man can never
        actually reach, ensuring pellets are only placed on reachable ground.

        Args:
            start_x (int): Column index of the flood-fill origin tile.
            start_y (int): Row index of the flood-fill origin tile.

        Returns:
            set[tuple[int, int]]: Set of (col, row) tile coordinates reachable
                from the start tile via walkable neighbours.
        """
        visited = set()
        visited.add((start_x, start_y))
        queue = deque([(start_x, start_y)])

        while queue:
            x, y = queue.popleft()

            neighbors = [
                (x + 1, y),
                (x - 1, y),
                (x, y + 1), 
                (x, y - 1)
            ]
            
            for nx, ny in neighbors:
                if (0 <= nx < self.map.width and 0 <= ny <self.map.height and
                    self.is_walkable(nx, ny) and (nx, ny) not in visited):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        return visited

    def get_valid_tiles(self, start_x: int = 1, start_y: int = 1) -> list[tuple[int, int]]:
        """
        Return all tile coordinates suitable for pellet or boost placement.

        A tile is valid if it is walkable, reachable from (start_x, start_y),
        and not inside the ghost pen.

        Args:
            start_x (int): Column index of the BFS origin used to determine
                reachability. Defaults to 1.
            start_y (int): Row index of the BFS origin used to determine
                reachability. Defaults to 1.

        Returns:
            list[tuple[int, int]]: List of (col, row) tile coordinates that
                are safe to place objects on.
        """
        reachable = self.find_reachable_tiles(start_x, start_y)
        valid = []

        for y, row in enumerate(self.map.level):
            for x, tile in enumerate(row):
                if not self.is_walkable(x, y):
                    continue
                if self.is_ghost_zone(x, y):
                    continue
                if (x, y) not in reachable:
                    continue
                valid.append((x, y))
        return valid

    def spawn_pellets(self, player=None):
        """
        Place one pellet on every valid tile and mark any already occupied
        by the player as eaten.

        If a player is supplied, pellets whose rects overlap the player's
        starting rect are immediately marked eaten so Pac-Man does not
        collect a pellet simply by spawning on top of it.

        Args:
            player (Pacman | None): The player sprite used for initial
                overlap checks. Pass None to skip the check. Defaults to None.

        Returns:
            None
        """
        valid_tiles = self.get_valid_tiles()
        self.pellets = [Pellet(x, y) for x, y in valid_tiles]

        if player:
            for pellet in self.pellets:
                if player.rect.colliderect(pellet.rect):
                    pellet.eaten = True

    def spawn_boost(self):
        """
        Place a randomly chosen boost on a random valid tile.

        Does nothing if a boost is already active (current_boost is not None).
        Removes the pellet occupying the chosen tile (if any) before placing
        the boost so the two objects do not overlap.

        Args:
            None

        Returns:
            None
        """
        if self.current_boost:
            return

        valid_tiles = self.get_valid_tiles()

        x, y = random.choice(valid_tiles)

        for pellet in self.pellets:
            if pellet.grid_x == x and pellet.grid_y == y:
                self.pellets.remove(pellet)
                break

        pixel_x = x * TILE_SIZE + TILE_SIZE // 2
        pixel_y = y * TILE_SIZE + TILE_SIZE // 2

        boost_class = random.choice([CakeBoost, StrawberryBoost, WatermelonBoost])
        self.current_boost = boost_class(pixel_x, pixel_y)
    
    def update_boost(self):
        """
        Rotate the active boost once boost_interval seconds have elapsed.

        Clears the current boost and spawns a new one, then resets
        last_boost_time. Called every frame from the main game loop.

        Args:
            None

        Returns:
            None
        """
        current_time = time.time()
        if current_time - self.last_boost_time >= self.boost_interval:
            self.current_boost = None
            self.spawn_boost()
            self.last_boost_time = current_time

    def draw_objects(self, screen):
        """
        Draw all uneaten pellets and the active boost onto the screen.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface.

        Returns:
            None
        """
        for pellet in self.pellets:
            if not pellet.eaten: 
                pellet.draw(screen)
        if self.current_boost:
            self.current_boost.draw(screen)
    
    def update_objects(self, player):
        """
        Detect and handle collection of pellets and the active boost.

        Pellet collection: each uneaten pellet is tested against a slightly
        inflated (4 px) copy of the player rect to give a forgiving hitbox.
        Collected pellets are marked eaten and the player scores 10 points.

        Boost collection: if the player's rect overlaps the active boost,
        apply_effect() is called and current_boost is cleared.

        Args:
            player (Pacman): The player sprite whose rect and score are
                updated on collection.

        Returns:
            None
        """
        for pellet in self.pellets:
            if not pellet.eaten and player.rect.inflate(4, 4).colliderect(pellet.rect):
                pellet.eaten = True
                player.score += 10

                now = time.time()

                if now - self.last_pellet_sfx_time >= self.pellet_sfx_cooldown:
                    player.sound_manager.play_sound("pacman_eat_dots")
                    self.last_pellet_sfx_time = now
        if self.current_boost and not self.current_boost.eaten:
            if player.rect.colliderect(self.current_boost.rect):
                self.current_boost.apply_effect(player)
                self.current_boost = None
                
                player.sound_manager.play_sound("pacman_eat_fruit")