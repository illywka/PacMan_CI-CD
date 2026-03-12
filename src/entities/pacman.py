import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
from src.audio.sound_manager import SoundManager
import src.entities.entity as entity
import time


class Pacman(pygame.sprite.Sprite):
    """
    Represents the Pacman player character with movement, animations,
    and game mechanics.

    This class handles player input and movement, sprite animations
    (movement in 4 directions and death sequence), life management
    and scoring, and power-up/boost effects.
    """

    def __init__(self, x, y, game_map, sound_manager=None):
        """
        Initialize Pacman at the specified position.

        Loads sprite animations, sets up initial position and state
        variables including lives, score, direction, speed, and
        active boosts.

        Args:
            self
            x (int): Starting x-coordinate in pixels
            y (int): Starting y-coordinate in pixels
            game_map: The game map object for collision detection
            sound_manager (SoundManager, optional): Sound manager instance

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
        Read keyboard state and queue the next intended movement direction.

        Supports both arrow keys and WASD. Only the most recent key in the
        priority order (left > right > up > down) is queued each frame.
        The queued direction is not applied immediately; move() validates
        it against walls at the next tile centre.

        Args:
            self

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
        Apply the queued direction and advance Pac-Man's position.

        Direction change rules:
            - An exact reverse (180°) is applied immediately.
            - Any other turn is only applied when Pac-Man is centred
              on a tile and the new direction is not blocked by a wall.

        Tunnel wrapping: exiting the left or right screen edge teleports
        Pac-Man to the opposite side.

        Args:
            self

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

                        c_tx = (self.rect.centerx // TILE_SIZE) * TILE_SIZE
                        c_ty = (self.rect.centery // TILE_SIZE) * TILE_SIZE

                        self.pos.x = c_tx
                        self.pos.y = c_ty
                        self.rect.topleft = (self.pos.x, self.pos.y)

                        if (
                            not entity.check_collision(
                                self, self.next_direction
                            )
                        ):
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
        Load sprite sheets and slice them into animation lists.
        """
        path_move = 'src/assets/pacman/pacman_move.png'
        path_death = 'src/assets/pacman/pacman_death.png'
        self.animations = {}

        try:
            sprite_sheet_move = pygame.image.load(
                path_move
            ).convert_alpha()

            sprite_sheet_death = pygame.image.load(
                path_death
            ).convert_alpha()

            move_f_count = 9
            death_f_count = 11

            m_width, m_height = sprite_sheet_move.get_size()
            move_frame_width = m_width / move_f_count

            d_width, d_height = sprite_sheet_death.get_size()
            death_frame_width = d_width / death_f_count

            move_frames = []
            death_frames = []

            for i in range(move_f_count):
                rect = pygame.Rect(
                    i * move_frame_width, 0,
                    move_frame_width, m_height
                )
                m_frame = sprite_sheet_move.subsurface(rect).copy()
                m_frame = pygame.transform.scale(
                    m_frame, (TILE_SIZE, TILE_SIZE)
                )
                move_frames.append(m_frame)

            for i in range(death_f_count):
                rect = pygame.Rect(
                    i * death_frame_width, 0,
                    death_frame_width, d_height
                )
                d_frame = sprite_sheet_death.subsurface(rect).copy()
                d_frame = pygame.transform.scale(
                    d_frame, (TILE_SIZE, TILE_SIZE)
                )
                death_frames.append(d_frame)

            self.animations["right"] = [
                move_frames[0], move_frames[1], move_frames[2], move_frames[1]
            ]
            self.animations["left"] = [
                move_frames[0], move_frames[3], move_frames[4], move_frames[3]
            ]
            self.animations["up"] = [
                move_frames[0], move_frames[5], move_frames[6], move_frames[5]
            ]
            self.animations["down"] = [
                move_frames[0], move_frames[7], move_frames[8], move_frames[7]
            ]
            self.animations["death"] = death_frames

            self.current_animation = self.animations["right"]

        except FileNotFoundError:
            print("Error: Sprite sheet not found at path")
            self.current_animation = [self.image]

    def animate(self):
        """
        Advance the animation frame for the current direction.
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
        Restore self.image and self.rect to their initial state.
        """
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(
            topleft=(self.start_pos.x, self.start_pos.y)
        )

    def update_boost(self):
        """
        Expire any active boosts whose timer has elapsed.
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
        Run all per-frame logic for Pac-Man.
        """
        self.get_input()
        self.move()
        self.animate()
        self.update_boost()
