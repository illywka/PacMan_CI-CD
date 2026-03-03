import pygame
import random

from src.audio.sound_manager import SoundManager
import src.entities.entity as entity
from src.utils.constants import (
    WIDTH, HEIGHT, TILE_SIZE, BLACK, WHITE, FPS,
    MAP_OFFSET_Y, GHOST_SPEED, DEFAULT_VOLUME, DIFFICULTY_SPEEDS,
)
from src.map.testMap import Map
from src.entities.pacman import Pacman
from src.entities.ghost import Pinky, Inky, Clyde, Sue
from src.map.randomized_map import RandomMap
from src.game_objects.object_manager import ObjectManager
from src.core.pause import Pause
from src.game_objects.volume_slider import VolumeSlider

class Game():
    """
    Main game controller for the Pac-Man clone.

    Manages the overall game lifecycle including state transitions,
    asset loading, event handling, rendering, and game logic updates.

    Attributes:
        screen (pygame.Surface): The main display surface.
        clock (pygame.time.Clock): Clock for controlling the frame rate.
        font (pygame.font.Font): Arcade-style font for score rendering.
        game_map (Map | RandomMap): The current level map.
        player (Pacman): The player-controlled Pac-Man sprite.
        ghosts_group (pygame.sprite.Group): Group containing all ghost sprites.
        objects (ObjectManager): Manages pellets and boost items.
        pause_menu (Pause): The in-game pause overlay.
        paused (bool): Whether the game is currently paused.
        escape_pressed (bool): Tracks ESC key state to prevent toggle repeat.
        ghost_speed (float): Base movement speed for all ghosts.
        game_state (str): Current state of the game FSM.
            One of: "menu", "settings", "game", "win", "lose".
    """

    def __init__(self, ghost_speed=GHOST_SPEED, initial_volume=DEFAULT_VOLUME):
        """
        Initialize Pygame, set up the display window, and prepare the game.

        Args:
            ghost_speed (float): Base movement speed for all ghosts.
            initial_volume (float): Initial volume level, between 0.0 and 1.0.

        Returns:
            None
        """

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('src/assets/font/arcadeclassic/ARCADECLASSIC.TTF', 28)

        self.sound_manager = SoundManager()
        self.sound_manager.play_sound_if_idle("pacman_menu_theme", loops=-1)

        self.volume_slider = VolumeSlider(center_x=WIDTH // 2, center_y=HEIGHT // 2 + 90)
        self.sound_manager.set_volume(self.volume_slider.get_volume())

        self.game_map = None
        self.player = None
        self.ghosts_group = None
        self.objects = None
        self.pause_menu = None
        self.paused = False
        self.escape_pressed = False
        self.ghost_speed = ghost_speed
        self.initial_volume = initial_volume
        self.game_state = "menu"
        self.running = True

        self.load_assets()
        self.init_game()

    def init_game(self):
        """
        Create and reset all game entities for a new session.

        Randomly selects either a fixed Map or a procedurally generated
        RandomMap. Spawns the player, all four ghosts, and populates the
        map with pellets.

        Returns:
            None
        """

        self.game_map = Map() if random.random() < 0.5 else RandomMap()

        self.player = Pacman(TILE_SIZE, TILE_SIZE, self.game_map, self.sound_manager)

        ghosts = [
            Pinky(self.game_map, self.player),
            Inky(self.game_map, self.player),
            Clyde(self.game_map, self.player),
            Sue(self.game_map, self.player),
        ]
        self.ghosts_group = pygame.sprite.Group(ghosts)
        self.update_ghost_speeds()

        self.objects = ObjectManager(self.game_map)
        self.objects.spawn_pellets(self.player)

        self.pause_menu = Pause(self.volume_slider)

    def load_assets(self):
        """
        Load all image assets, create button rects, and build the
        difficulty button lookup table.

        Returns:
            None
        """

        self.startpage_img = self._load_image('src/assets/interface/startpage/startpage.png', scale=(WIDTH, HEIGHT))

        self.play_btn_img = self._load_image('src/assets/interface/play_button/play_button.png')
        self.menu_btn_img = self._load_image('src/assets/interface/menu_button/menu_button.png')
        self.play_btn_rect = self.play_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.menu_btn_rect = self.menu_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + self.play_btn_img.get_height()))

        self.easy_mode_btn_img = self._load_image('src/assets/interface/lvl_difficulty/easy_lvl.png')
        self.medium_mode_btn_img = self._load_image('src/assets/interface/lvl_difficulty/medium_lvl.png')
        self.hard_mode_btn_img = self._load_image('src/assets/interface/lvl_difficulty/hard_lvl.png')
        self.easy_mode_btn_rect = self.easy_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.medium_mode_btn_rect = self.medium_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.hard_mode_btn_rect = self.hard_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        self.pause_btn_img = self._load_image('src/assets/interface/pause_button/pause_button.png')
        self.pause_btn_rect = self.pause_btn_img.get_rect(topright=(WIDTH - 15, 7))

        self.arrow_btn_img = self._load_image('src/assets/interface/arrow/arrow.png')
        self.arrow_btn_rect = self.arrow_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

        self.volume_slider = VolumeSlider(center_x=WIDTH // 2, center_y=HEIGHT // 2 + 90, initial_volume=self.initial_volume)

        self.losepage_img = self._load_image('src/assets/interface/lose_page/lose_menu.png', scale=(WIDTH, HEIGHT))
        self.winpage_img = self._load_image('src/assets/interface/win_page/win_menu.png', scale=(WIDTH, HEIGHT))

        self.again_btn_img = self._load_image('src/assets/interface/again_button/again_button.png')
        self.again_btn_rect = self.again_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 78))

        self.exit_btn_img = self._load_image('src/assets/interface/exit_button/exit_button.png')
        self.exit_btn_rect = self.exit_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 125))

        self._difficulty_buttons = [
            (self.easy_mode_btn_rect, "easy"),
            (self.medium_mode_btn_rect, "medium"),
            (self.hard_mode_btn_rect, "hard"),
        ]

    @staticmethod
    def _load_image(path, scale=None):
        """
        Load an image and optionally scale it.

        Args:
            path (str): File path to the image.
            scale (tuple[int, int] | None): Target (width, height), or
                None to keep the original size.

        Returns:
            pygame.Surface: The loaded (and optionally scaled) surface.
        """

        image = pygame.image.load(path).convert_alpha()

        if scale is not None:
            image = pygame.transform.scale(image, scale)

        return image

    def _play_click_sound(self):
        """Play the shared UI button-click sound effect."""

        self.sound_manager.play_sound("game_select_button")

    def _update_ghost_sounds(self):
        """
        Switch between the three mutually exclusive ghost sound layers
        (scared / returning / normal) based on current game state.

        Returns:
            None
        """

        any_ghost_dead = any(ghost.is_dead for ghost in self.ghosts_group)

        if self.player.shielded:
            self.sound_manager.stop_sound("ghosts_normal_move")
            self.sound_manager.stop_sound("ghosts_return_to_house")
            self.sound_manager.play_sound_if_idle("ghosts_turn_to_blue", loops=-1)
        elif not any_ghost_dead:
            self.sound_manager.stop_sound("ghosts_turn_to_blue")
            self.sound_manager.stop_sound("ghosts_return_to_house")
            self.sound_manager.play_sound_if_idle("ghosts_normal_move", loops=-1)
        else:
            self.sound_manager.stop_sound("ghosts_turn_to_blue")
            self.sound_manager.stop_sound("ghosts_normal_move")
            self.sound_manager.play_sound_if_idle("ghosts_return_to_house", loops=-1)

    def _reset_all_entities(self):
        """
        Reset the player and every ghost back to their spawn positions.

        Returns:
            None
        """

        entity.reset_position(self.player)

        for ghost in self.ghosts_group:
            ghost.spawn_time = pygame.time.get_ticks()
            ghost.is_dead = False
            ghost.is_scared = False
            ghost.path = []
            entity.reset_position(ghost)

    def update_ghost_speeds(self):
        """
        Apply the current ghost_speed setting to every ghost in the group.

        Returns:
            None
        """

        for ghost in self.ghosts_group:
            ghost.base_speed = self.ghost_speed
            ghost.speed = self.ghost_speed

    def _draw_end_screen(self, background_img):
        """
        Render a win or lose end screen with again/exit buttons.

        Args:
            background_img (pygame.Surface): Full-screen background artwork.

        Returns:
            None
        """

        self.screen.blit(background_img, (0, 0))
        self.screen.blit(self.again_btn_img, self.again_btn_rect)
        self.screen.blit(self.exit_btn_img, self.exit_btn_rect)

    def draw_score(self):
        """
        Render the player's score centred in the HUD area above the map.

        Returns:
            None
        """

        score_text = self.font.render(str(self.player.score), True, WHITE)
        score_rect = score_text.get_rect(center=(WIDTH // 2, MAP_OFFSET_Y // 2))
        self.screen.blit(score_text, score_rect)

    def play_death_animation(self):
        """
        Play the death animation frame-by-frame at 7 FPS.

        Returns:
            None
        """

        self.sound_manager.stop_sound("ghosts_normal_move")
        self.sound_manager.stop_sound("ghosts_return_to_house")
        self.sound_manager.play_sound("pacman_death")

        self.update_ghost_speeds()

        for frame in self.player.animations["death"]:
            for event in pygame.event.get():
                self.volume_slider.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.screen.fill(BLACK)
            self.game_map.draw_map(self.screen)

            for ghost in self.ghosts_group:
                self.screen.blit(ghost.image, ghost.rect.move(0, MAP_OFFSET_Y))

            self.screen.blit(frame, self.player.rect.move(0, MAP_OFFSET_Y))
            pygame.display.flip()
            self.clock.tick(7)

    def _handle_events(self):
        """
        Process all queued Pygame events for the current frame.

        Returns:
            None
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            self.volume_slider.handle_event(event)

            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                self.sound_manager.set_volume(self.volume_slider.get_volume())

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.game_state == "game" and not self.escape_pressed:
                    self._play_click_sound()
                    self.paused = not self.paused
                    self.escape_pressed = True

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.escape_pressed = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event)

    def _handle_click(self, event):
        """
        Route a MOUSEBUTTONDOWN event to the correct state handler.

        Args:
            event (pygame.event.Event): The click event.

        Returns:
            None
        """

        if self.game_state == "menu":
            self._handle_menu_click(event)
        elif self.game_state == "settings":
            self._handle_settings_click(event)
        elif self.game_state in ("win", "lose"):
            self._handle_end_screen_click(event)
        elif self.game_state == "game":
            self._handle_game_click(event)

    def _handle_menu_click(self, event):
        """Handle clicks on the main-menu screen."""

        if self.play_btn_rect.collidepoint(event.pos):
            self._play_click_sound()
            self.sound_manager.stop_sound("pacman_menu_theme")
            self.init_game()
            self.game_state = "game"
        elif self.menu_btn_rect.collidepoint(event.pos):
            self._play_click_sound()
            self.game_state = "settings"

    def _handle_settings_click(self, event):
        """Handle clicks on the settings / difficulty screen."""

        if self.arrow_btn_rect.collidepoint(event.pos):
            self._play_click_sound()
            self.game_state = "menu"

            return

        for btn_rect, difficulty in self._difficulty_buttons:
            if btn_rect.collidepoint(event.pos):
                self._play_click_sound()
                self.ghost_speed = DIFFICULTY_SPEEDS[difficulty]
                self.game_state = "menu"

                return

    def _handle_end_screen_click(self, event):
        """Handle clicks on the win / lose screen."""

        if self.again_btn_rect.collidepoint(event.pos):
            self.sound_manager.stop_all_sounds()
            self._play_click_sound()
            self.init_game()
            self.game_state = "game"
        elif self.exit_btn_rect.collidepoint(event.pos):
            self.sound_manager.stop_all_sounds()
            self._play_click_sound()
            self.game_state = "menu"

    def _handle_game_click(self, event):
        """Handle clicks during active gameplay (pause toggle & menu)."""

        if self.pause_btn_rect.collidepoint(event.pos):
            self._play_click_sound()
            self.paused = not self.paused

        if self.paused:
            self.sound_manager.stop_all_sounds()
            result = self.pause_menu.handle_event(event)

            if result == 'continue':
                self._play_click_sound()
                self.paused = False
            elif result == 'exit':
                self._play_click_sound()
                self.game_state = "menu"
                self.paused = False

    def _update(self):
        """
        Advance one frame of game logic (only when playing and unpaused).

        Returns:
            None
        """

        if self.game_state != "game" or self.paused:
            return

        self.player.update()
        self.ghosts_group.update()
        self.objects.update_boost()
        self.objects.update_objects(self.player)

        for ghost in self.ghosts_group:
            ghost.is_scared = self.player.shielded

        self._update_ghost_sounds()
        self._handle_collisions()
        self._check_win_condition()

    def _handle_collisions(self):
        """
        Detect and resolve player–ghost collisions.

        Returns:
            None
        """

        collisions = pygame.sprite.spritecollide(self.player, self.ghosts_group, False)
        alive_collisions = [g for g in collisions if not g.is_dead]

        if not alive_collisions:
            return

        ghost = alive_collisions[0]

        if self.player.shielded:
            ghost.is_scared = False
            ghost.is_dead = True
            self.player.shielded = False
            del self.player.active_boosts["shield"]
        else:
            self.player.lives -= 1
            self.play_death_animation()
            pygame.time.delay(300)

            if self.player.lives <= 0:
                self.sound_manager.play_sound("pacman_lose")
                self.game_state = "lose"
            else:
                self._reset_all_entities()

    def _check_win_condition(self):
        """Transition to the win state if every pellet has been eaten."""

        if all(pellet.eaten for pellet in self.objects.pellets):
            self.sound_manager.stop_all_sounds()
            self.sound_manager.play_sound_if_idle("pacman_win")
            self.game_state = "win"

    def _draw(self):
        """
        Render the current frame based on the active game state.

        Returns:
            None
        """

        if self.game_state == "menu":
            self._draw_menu()
        elif self.game_state == "settings":
            self._draw_settings()
        elif self.game_state == "win":
            self._draw_end_screen(self.winpage_img)
        elif self.game_state == "lose":
            self._draw_end_screen(self.losepage_img)
        elif self.game_state == "game":
            self._draw_game()

        pygame.display.flip()

    def _draw_menu(self):
        """Render the main-menu screen."""

        self.sound_manager.play_sound_if_idle("pacman_menu_theme", loops=-1)
        self.screen.blit(self.startpage_img, (0, 0))
        self.screen.blit(self.play_btn_img, self.play_btn_rect)
        self.screen.blit(self.menu_btn_img, self.menu_btn_rect)

    def _draw_settings(self):
        """Render the settings / difficulty selection screen."""

        self.screen.fill(BLACK)
        self.screen.blit(self.easy_mode_btn_img, self.easy_mode_btn_rect)
        self.screen.blit(self.medium_mode_btn_img, self.medium_mode_btn_rect)
        self.screen.blit(self.hard_mode_btn_img, self.hard_mode_btn_rect)
        self.screen.blit(self.arrow_btn_img, self.arrow_btn_rect)
        self.volume_slider.draw(self.screen)

    def _draw_game(self):
        """Render the active gameplay screen, including pause overlay."""

        self.screen.fill(BLACK)
        self.game_map.draw_map(self.screen)
        self.objects.draw_objects(self.screen)
        self.screen.blit(self.player.image, self.player.rect.move(0, MAP_OFFSET_Y))

        for ghost in self.ghosts_group:
            self.screen.blit(ghost.image, ghost.rect.move(0, MAP_OFFSET_Y))

        self.draw_score()

        if self.paused:
            self.pause_menu.draw(self.screen)
        else:
            self.screen.blit(self.pause_btn_img, self.pause_btn_rect)

    def run(self):
        """
        Run the main game loop until the window is closed.

        Each iteration: handle events → update logic → draw frame.
        Capped at FPS frames per second.

        Returns:
            None
        """

        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

        pygame.quit()