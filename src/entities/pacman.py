import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
from src.audio.sound_manager import SoundManager
import src.entities.entity as entity
import time

class Pacman(pygame.sprite.Sprite):
    """
    Represents the Pacman player character with movement, animations, and game mechanics.

    This class handles player input and movement, sprite animations (movement in
    4 directions and death sequence), life management and scoring, and power-up/boost
    effects.
    """

    def __init__(self, x, y, game_map, sound_manager = None):
        """
        Initialize Pacman at the specified position.

        Loads sprite animations, sets up initial position and state variables
        including lives, score, direction, speed, and active boosts.

        Args:
            x (int): Starting x-coordinate in pixels
            y (int): Starting y-coordinate in pixels
            game_map: The game map object for collision detection
            sound_manager (SoundManager, optional): Sound manager instance for audio

        Returns:
            None
        """

        super().__init__()
        self.sound_manager = sound_manager or SoundManager()
        self.import_assets()

        self.frame_index = 0
        self.animation_speed = 0.1
        self.image = self.current_animation[self.frame_index]
        self.original_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.game_map = game_map
        self.direction = pygame.Vector2(0, 0)
        self.next_direction = pygame.Vector2(0, 0)
        self.speed = PACMAN_SPEED
        self.lives = 3
        self.score = 0
        
        self.active_boosts = {}
        self.base_speed = PACMAN_SPEED
        self.shielded = False

        self.pos = pygame.Vector2(self.rect.topleft)
        self.start_pos = self.pos.copy()

    def get_input(self):
        """
        Process keyboard input and set the next movement direction.

        Checks for arrow keys or WASD keys and updates the next_direction
        vector accordingly. The next direction will be applied when Pacman
        reaches a tile center, allowing for smooth directional changes.

        Args:
            None

        Returns:
            None
        """

        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.next_direction = pygame.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.next_direction = pygame.Vector2(1, 0)
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            self.next_direction = pygame.Vector2(0, -1)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.next_direction = pygame.Vector2(0, 1)

    def move(self):
        """
        Update Pacman's position based on current direction and handle collisions.

        Handles direction changes when Pacman is centered on a tile,
        implements screen wrapping at the edges, checks for wall collisions,
        and updates the position smoothly. Snaps to tile boundaries when
        collision is detected.

        Args:
            None

        Returns:
            None
        """

        if self.next_direction != pygame.Vector2(0, 0):
            if self.next_direction == -self.direction:
                self.direction = self.next_direction
                self.next_direction = pygame.Vector2(0, 0)

            elif entity.is_centered(self):
                if self.direction != self.next_direction:
                    if 0 <= self.rect.centerx < WIDTH:
                        old_pos = self.pos.copy()
                        old_rect_topleft = self.rect.topleft

                        current_tile_x = (self.rect.centerx // TILE_SIZE) * TILE_SIZE
                        current_tile_y = (self.rect.centery // TILE_SIZE) * TILE_SIZE

                        self.pos.x = current_tile_x
                        self.pos.y = current_tile_y
                        self.rect.topleft = (self.pos.x, self.pos.y)

                        if not entity.check_collision(self, self.next_direction):
                            self.direction = self.next_direction
                            self.next_direction = pygame.Vector2(0, 0)
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

    def import_assets(self):
        """
        Load and prepare all Pacman sprite animations.

        Loads two sprite sheets: movement sprites (9 frames for directional
        movement left, right, up, down) and death animation (11 frames showing
        Pacman's death sequence). Each frame is extracted from the sprite sheet,
        scaled to TILE_SIZE, and organized into animation dictionaries by direction.

        Args:
            None

        Returns:
            None
        """

        path_move = 'src/assets/pacman/pacman_move.png'
        path_death = 'src/assets/pacman/pacman_death.png'
        self.animations = {}

        try:
            sprite_sheet_move = pygame.image.load(path_move).convert_alpha()
            sprite_sheet_death = pygame.image.load(path_death).convert_alpha()

            move_frame_count = 9
            death_frame_count = 11

            move_sheet_width, move_sheet_height = sprite_sheet_move.get_size()
            move_frame_width = move_sheet_width / move_frame_count

            death_sheet_width, death_sheet_height = sprite_sheet_death.get_size()
            death_frame_width = death_sheet_width / death_frame_count

            move_frames = []
            death_frames = []

            for i in range(move_frame_count):
                rect = pygame.Rect(i * move_frame_width, 0, move_frame_width, move_sheet_height)

                move_frame = sprite_sheet_move.subsurface(rect).copy()
                move_frame = pygame.transform.scale(move_frame, (TILE_SIZE, TILE_SIZE))

                move_frames.append(move_frame)

            for i in range(death_frame_count):
                rect = pygame.Rect(i * death_frame_width, 0, death_frame_width, death_sheet_height)

                death_frame = sprite_sheet_death.subsurface(rect).copy()
                death_frame = pygame.transform.scale(death_frame, (TILE_SIZE, TILE_SIZE))

                death_frames.append(death_frame)

            self.animations["right"] = [move_frames[0], move_frames[1], move_frames[2], move_frames[1]]
            self.animations["left"] = [move_frames[0], move_frames[3], move_frames[4], move_frames[3]]
            self.animations["up"] = [move_frames[0], move_frames[5], move_frames[6], move_frames[5]]
            self.animations["down"] = [move_frames[0], move_frames[7], move_frames[8], move_frames[7]]
            self.animations["death"] = death_frames

            self.current_animation = self.animations["right"]

        except FileNotFoundError:
            print(f"Error: Sprite sheet not found at path")

            self.current_animation = [self.image]

    def animate(self):
        """
        Update Pacman's sprite animation based on current movement direction.

        Selects the appropriate animation sequence (left, right, up, down)
        based on the current direction vector. Advances the frame index
        when Pacman is moving, creating smooth directional animations.
        The death animation sequence is handled separately.

        Args:
            None

        Returns:
            None
        """

        if self.direction == pygame.Vector2(-1, 0):
            self.current_animation = self.animations["left"]
        elif self.direction == pygame.Vector2(1, 0):
            self.current_animation = self.animations["right"]
        elif self.direction == pygame.Vector2(0, -1):
            self.current_animation = self.animations["up"]
        elif self.direction == pygame.Vector2(0, 1):
            self.current_animation = self.animations["down"]

        if self.direction.magnitude() != 0:
            self.frame_index += self.animation_speed

            if self.frame_index >= len(self.current_animation):
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.current_animation[int(self.frame_index)]

    def reset_image(self):
        """
        Reset Pacman's sprite to the original image and starting position.

        Restores the initial sprite image and repositions Pacman's rectangle
        to the starting position. Used when respawning after losing a life.

        Args:
            None

        Returns:
            None
        """

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft = (self.start_pos.x, self.start_pos.y))
    
    def update_boost(self):
        """
        Check and expire active power-up effects based on elapsed time.

        Monitors the duration of active boosts (speed and shield) and removes
        them when they expire. Resets speed to base value when speed boost
        ends and disables shield when shield boost expires.

        Args:
            None

        Returns:
            None
        """

        current_time = time.time()

        if "speed" in self.active_boosts:
            if current_time > self.active_boosts["speed"]:
                del self.active_boosts["speed"]
                self.speed = self.base_speed
        if "shield" in self.active_boosts:
            if current_time > self.active_boosts["shield"]:
                del self.active_boosts["shield"]
                self.shielded = False

    def update(self):
        """
        Main update loop called every frame to update Pacman's state.

        Executes all per-frame updates in sequence: processes input,
        updates position, advances animation frame, and checks boost
        expiration. This is the main entry point for updating Pacman
        during gameplay.

        Args:
            None

        Returns:
            None
        """

        self.get_input()
        self.move()
        self.animate()
        self.update_boost()