import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
import src.entities.entity as entity
import time

class Pacman(pygame.sprite.Sprite):
    """
    Player-controlled Pac-Man sprite.

    Handles keyboard input, tile-aligned movement with tunnel wrapping,
    frame animation, boost timers, and tracks lives and score.

    Attributes:
        frame_index (float): Fractional index into the current animation list,
            incremented each frame by animation_speed.
        animation_speed (float): Amount added to frame_index per update cycle.
        image (pygame.Surface): The currently displayed animation frame.
        original_image (pygame.Surface): Unmodified copy of the initial frame,
            used by reset_image() to restore appearance after death.
        rect (pygame.Rect): Bounding box used for rendering and collision.
        game_map (Map | RandomMap): Reference to the active level map.
        direction (pygame.Vector2): Unit vector of current movement direction.
        next_direction (pygame.Vector2): Queued direction to apply at the next
            valid tile centre.
        speed (float): Current per-frame pixel speed; may be boosted temporarily.
        lives (int): Remaining lives; game ends when this reaches 0.
        score (int): Accumulated score from eating pellets and boosts.
        active_boosts (dict[str, float]): Maps active boost name to its
            expiry timestamp (time.time()).
        base_speed (float): Reference speed used to restore after a speed boost.
        shielded (bool): True while a shield boost is active.
        pos (pygame.Vector2): Sub-pixel position used for smooth movement.
        start_pos (pygame.Vector2): Spawn position, used by reset_position().
        animations (dict[str, list[pygame.Surface]]): Keyed animation frame
            lists: "right", "left", "up", "down", "death".
        current_animation (list[pygame.Surface]): The animation list currently
            being cycled through.
    """
    def __init__(self, x: int, y: int, game_map):
        """
        Initialise Pac-Man at the given tile coordinates.

        Loads and slices sprite sheets into named animation lists, sets all
        movement and boost state to their defaults, and records the spawn
        position for later resets.

        Args:
            x (int): Starting pixel x coordinate (left edge of sprite).
            y (int): Starting pixel y coordinate (top edge of sprite).
            game_map (Map | RandomMap): The active level map, used for wall
                collision checks.

        Returns:
            None
        """
        super().__init__()
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
        The queued direction is not applied immediately; move() validates it
        against walls at the next tile centre.

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
        Apply the queued direction and advance Pac-Man's position by one frame.

        Direction change rules:
            - An exact reverse (180°) is applied immediately without waiting
              for a tile centre.
            - Any other turn is only applied when Pac-Man is centred on a tile
              and the new direction is not blocked by a wall.

        Tunnel wrapping: exiting the left or right screen edge teleports
        Pac-Man to the opposite side.

        Movement: if the current direction is clear, pos advances by speed
        pixels. If blocked, pos snaps to the current tile centre to prevent
        wall clipping.

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
        Load sprite sheets from disk and slice them into named animation lists.

        Loads two sprite sheets: a 9-frame movement sheet and an 11-frame
        death sheet. Each frame is cropped to its natural width and scaled to
        TILE_SIZE × TILE_SIZE. The resulting frames are assembled into the
        directional animation lists stored in self.animations.

        Animation keys and their frame composition:
            "right"  — frames 0, 1, 2, 1  (mouth opening right)
            "left"   — frames 0, 3, 4, 3  (mouth opening left)
            "up"     — frames 0, 5, 6, 5  (mouth opening up)
            "down"   — frames 0, 7, 8, 7  (mouth opening down)
            "death"  — all 11 death frames in order

        Falls back to a single-frame animation using the current image if
        either sprite sheet file is not found.

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
        Advance the animation frame and update self.image for the current direction.

        Switches current_animation to match the movement direction, then
        increments frame_index by animation_speed. When moving, the index
        wraps back to 0 after the last frame. When stationary, the index is
        held at 0 (the closed-mouth frame).

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
        Restore self.image and self.rect to their initial state.

        Copies original_image back to image and repositions rect to
        start_pos. Called after a death animation completes so Pac-Man
        reappears at his spawn tile with the default closed-mouth sprite.

        Args:
            None

        Returns:
            None
        """
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft = (self.start_pos.x, self.start_pos.y))
    
    def update_boost(self):
        """
        Expire any active boosts whose timer has elapsed.

        Checks each boost in active_boosts against the current wall-clock
        time. Expired boosts are removed from the dict and their associated
        state is reverted:
            - "speed" boost: self.speed is reset to base_speed.
            - "shield" boost: self.shielded is set to False.

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
        Run all per-frame logic for Pac-Man.

        Calls, in order: get_input(), move(), animate(), update_boost().
        Intended to be called once per game loop iteration by the main
        Game class.

        Args:
            None

        Returns:
            None
        """
        self.get_input()
        self.move()
        self.animate()
        self.update_boost()