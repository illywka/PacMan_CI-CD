import pygame
from src.utils.constants import TILE_SIZE

def is_centered(self) -> bool:
        """
        Check whether the entity is close enough to the centre of its current tile.

        Computes the nearest tile centre from the entity's pixel position and
        returns True if the distance in both axes is within a tolerance equal
        to the entity's current speed. This is used to gate direction changes
        so entities only turn at tile boundaries, preventing clipping into walls.

        Args:
                None

        Returns:
                bool: True if the entity is within one speed-unit of the tile centre
                on both axes, False otherwise.
        """
        center_x, center_y = self.rect.center

        tile_center_x = (center_x // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = (center_y // TILE_SIZE) * TILE_SIZE + TILE_SIZE // 2

        dist_x = abs(center_x - tile_center_x)
        dist_y = abs(center_y - tile_center_y)

        tolerance = self.speed

        return dist_x < tolerance and dist_y < tolerance

def check_collision(self, direction) -> bool:
        """
        Determine whether moving one step in the given direction would collide
        with a wall tile.

        Projects the entity's bounding rect forward by one speed-unit along
        the supplied direction vector and tests it against every wall rect in
        the current map. The entity's actual position is not modified.

        Args:
                direction (pygame.Vector2): A unit (or zero) vector representing
                the intended movement direction, e.g. Vector2(1, 0) for right.

        Returns:
                bool: True if the projected rect overlaps any wall tile, False if
                the path is clear.
        """
        next_x = self.pos.x + direction.x * self.speed
        next_y = self.pos.y + direction.y * self.speed

        next_rect = pygame.Rect(next_x, next_y, self.rect.width, self.rect.height)

        if next_rect.collidelist(self.game_map.walls) > -1:
            return True

        return False

def reset_position(self) -> None:
        """
        Teleport the entity back to its spawn position and clear its movement state.

        Resets the pixel-accurate position vector and the display rect to the
        entity's original starting coordinates, and zeroes both the current
        direction and the queued next direction. Called after the player loses a
        life or when starting a new round so all entities begin from their
        designated spawn points.

        Args:
                None

        Returns:
                None
        """
        self.rect.topleft = self.start_pos.copy()

        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)

        self.pos = self.start_pos.copy()
