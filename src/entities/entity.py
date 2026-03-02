import pygame
from src.utils.constants import TILE_SIZE, GHOST_SPEED

def is_centered(self):
        """
        Check if the entity is centered within its current tile.

        Calculates the distance between the entity's center and the tile's
        center point. Returns True if the entity is within a tolerance
        distance (equal to its speed) from the tile center. Used to determine
        when the entity can make direction changes.

        Args:
            self: The entity instance (Pacman or Ghost)

        Returns:
            bool: True if entity is centered on a tile, False otherwise
        """

        center_x, center_y = self.rect.center

        tile_center_x = (center_x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2    
        tile_center_y = (center_y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2

        dist_x = abs(center_x - tile_center_x)
        dist_y = abs(center_y - tile_center_y)

        tolerance = self.speed

        return dist_x < tolerance and dist_y < tolerance

def check_collision(self, direction):
        """
        Check if moving in the given direction would result in a wall collision.

        Calculates the entity's next position based on the provided direction
        and current speed, then checks if that position would collide with any
        walls on the game map.

        Args:
            self: The entity instance (Pacman or Ghost)
            direction (pygame.Vector2): The direction vector to check for collision

        Returns:
            bool: True if collision would occur, False if path is clear
        """

        next_x = self.pos.x + direction.x * self.speed
        next_y = self.pos.y + direction.y * self.speed
        
        next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)

        if next_rect.collidelist(self.game_map.walls) > -1:
            return True
        
        return False

def reset_position(self):
        """
        Reset the entity to its starting position and clear movement directions.

        Restores the entity's position to the initial starting position,
        resets both current and next direction vectors to zero (no movement),
        and updates the position vector. Used when respawning entities or
        resetting game state.

        Args:
            self: The entity instance (Pacman or Ghost)

        Returns:
            None
        """

        self.rect.topleft = self.start_pos.copy()

        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)

        self.pos = self.start_pos.copy()