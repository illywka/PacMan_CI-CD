import pygame, os, time
from abc import ABC, abstractmethod
from src.utils.constants import PACMAN_SPEED, BOOST_DURATION, MAP_OFFSET_Y

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "boosts")
BOOST_CONFIGS = {
    "CakeBoost": "cake",
    "StrawberryBoost": "strawberry",
    "WatermelonBoost": "watermelon"
}
"""
dict[str, str]: Maps each Boost subclass name to the subdirectory and
base filename used to locate its sprite under ASSETS_PATH.
"""

class Boost(ABC):
    """
    Abstract base class for all collectible boost items.

    Handles shared image loading with per-subclass caching, positioning,
    draw logic, and the eaten flag. Each concrete subclass implements
    apply_effect() to define what happens when Pac-Man collects it.

    Class Attributes:
        _images (dict[str, pygame.Surface]): Class-level cache mapping
            subclass names to their loaded surfaces, so each sprite is
            loaded from disk only once regardless of how many instances
            are created.

    Attributes:
        x (int): Pixel x coordinate of the boost's centre.
        y (int): Pixel y coordinate of the boost's centre.
        image (pygame.Surface): The sprite surface for this boost type,
            retrieved from the class-level cache.
        rect (pygame.Rect): Bounding rect centred on (x, y), used for
            rendering and collision detection.
        eaten (bool): True once Pac-Man has collected this boost; eaten
            boosts are neither drawn nor re-applied.
    """
    _images = {}
    def __init__(self, x: int, y: int):
        """
        Initialise the boost at the given pixel coordinates.

        Looks up the subclass name in BOOST_CONFIGS to find the correct
        asset folder and filename, then loads and caches the image if it
        has not been loaded before.

        Args:
            x (int): Pixel x coordinate for the centre of the boost sprite.
            y (int): Pixel y coordinate for the centre of the boost sprite.

        Returns:
            None
        """
        self.x = x
        self.y = y

        class_name = self.__class__.__name__
        if class_name not in Boost._images:
            folder = BOOST_CONFIGS[class_name]
            file_path = os.path.join(ASSETS_PATH, folder, f"{folder}.png")
            Boost._images[class_name] = pygame.image.load(file_path).convert_alpha()

        self.image = Boost._images[class_name]
        self.rect = self.image.get_rect(center=(x,y))
        self.eaten = False
    
    def draw(self, screen):
        """
        Blit the boost sprite onto the screen if it has not been eaten.

        Applies the MAP_OFFSET_Y vertical shift so the sprite aligns with
        the play area below the HUD.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface.

        Returns:
            None
        """
        if not self.eaten:
            shifted_rect = self.rect.move(0, MAP_OFFSET_Y)
            screen.blit(self.image, shifted_rect)
    
    @abstractmethod
    def apply_effect(self, pacman):
        """
        Apply this boost's effect to the player.

        Called by ObjectManager the moment Pac-Man's rect overlaps this
        boost's rect. Subclasses modify pacman's state directly (speed,
        score, shielded, active_boosts, etc.).

        Args:
            pacman (Pacman): The player sprite to apply the effect to.

        Returns:
            None
        """
        pass


class CakeBoost(Boost):
    """
    Speed boost — temporarily increases Pac-Man's movement speed.

    Raises speed by 2 pixels per frame above PACMAN_SPEED for
    BOOST_DURATION seconds, tracked via the "speed" entry in
    pacman.active_boosts.
    """
    def apply_effect(self, pacman):
        """
        Increase Pac-Man's speed and register the boost expiry time.

        Args:
            pacman (Pacman): The player sprite to apply the effect to.

        Returns:
            None
        """
        pacman.speed = PACMAN_SPEED + 2
        pacman.active_boosts["speed"] = time.time() + BOOST_DURATION

class StrawberryBoost(Boost):
    """
    Score boost — instantly awards 1000 points with no timed effect.
    """
    def apply_effect(self, pacman):
        """
        Add 1000 points to Pac-Man's score.

        Args:
            pacman (Pacman): The player sprite to apply the effect to.

        Returns:
            None
        """
        pacman.score += 1000  #можна змінити з часом

class WatermelonBoost(Boost):
    """
    Shield boost — grants Pac-Man a temporary one-hit shield.

    While shielded, the next ghost collision kills the ghost instead of
    costing a life. The shield expires after BOOST_DURATION seconds or
    on first use, whichever comes first.
    """
    def apply_effect(self, pacman):
        """
        Activate Pac-Man's shield and register the boost expiry time.

        Args:
            pacman (Pacman): The player sprite to apply the effect to.

        Returns:
            None
        """
        pacman.shielded = True
        pacman.active_boosts["shield"] = time.time() + BOOST_DURATION