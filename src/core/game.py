import pygame
import random

from src.audio.sound_manager import SoundManager
import src.entities.entity as entity
from src.utils.constants import WIDTH, HEIGHT, TILE_SIZE, BLACK, FPS, MAP_OFFSET_Y, GHOST_SPEED, DEFAULT_VOLUME
from src.map.testMap import Map
from src.entities.pacman import Pacman
from src.entities.ghost import Pinky, Inky, Clyde, Sue
from src.map.randomized_map import RandomMap
from src.game_objects.object_manager import ObjectManager
from src.core.pause import Pause
from src.game_objects.volume_slider import VolumeSlider

class Game():
    def __init__(self, ghost_speed = GHOST_SPEED, initial_volume = DEFAULT_VOLUME):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('src/assets/font/arcadeclassic/ARCADECLASSIC.TTF', 28)

        self.sound_manager = SoundManager()
        self.sound_manager.play_sound_if_idle("pacman_menu_theme", loops = -1)

        self.volume_slider = VolumeSlider(center_x = WIDTH // 2, center_y = HEIGHT // 2 + 90)
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

        self.load_assets()
        self.init_game()
    
    def init_game(self):
        if random.random() < 0.5:
            self.game_map = Map()
        else:
            self.game_map = RandomMap()

        self.player = Pacman(TILE_SIZE, TILE_SIZE, self.game_map, self.sound_manager)

        ghosts = [ 
            Pinky(self.game_map, self.player),
            Inky(self.game_map, self.player),
            Clyde(self.game_map, self.player),
            Sue(self.game_map, self.player)
        ]
        self.ghosts_group = pygame.sprite.Group(ghosts)
        for ghost in self.ghosts_group:
            ghost.base_speed = self.ghost_speed
            ghost.speed = self.ghost_speed

        self.objects = ObjectManager(self.game_map)
        self.objects.spawn_pellets(self.player)

        self.pause_menu = Pause(self.volume_slider) 

    def load_assets(self):
        self.startpage_img = pygame.image.load('src/assets/interface/startpage/startpage.png').convert_alpha()
        self.startpage_img = pygame.transform.scale(self.startpage_img, (WIDTH, HEIGHT))

        self.play_btn_img = pygame.image.load('src/assets/interface/play_button/play_button.png').convert_alpha()
        self.menu_btn_img = pygame.image.load('src/assets/interface/menu_button/menu_button.png').convert_alpha()

        self.play_btn_rect = self.play_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.menu_btn_rect = self.menu_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + self.play_btn_img.get_height()))

        self.easy_mode_btn_img = pygame.image.load('src/assets/interface/lvl_difficulty/easy_lvl.png').convert_alpha()
        self.medium_mode_btn_img = pygame.image.load('src/assets/interface/lvl_difficulty/medium_lvl.png').convert_alpha()
        self.hard_mode_btn_img = pygame.image.load('src/assets/interface/lvl_difficulty/hard_lvl.png').convert_alpha()

        self.easy_mode_btn_rect = self.easy_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        self.medium_mode_btn_rect = self.medium_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
        self.hard_mode_btn_rect = self.hard_mode_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))

        self.pause_btn_img = pygame.image.load('src/assets/interface/pause_button/pause_button.png').convert_alpha()
        self.pause_btn_rect = self.pause_btn_img.get_rect(topright=(WIDTH - 15, 7))

        self.arrow_btn_img = pygame.image.load('src/assets/interface/arrow/arrow.png').convert_alpha()
        self.arrow_btn_rect = self.arrow_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))

        self.volume_slider = VolumeSlider(center_x=WIDTH // 2, center_y=HEIGHT // 2 + 90, initial_volume=self.initial_volume)
        self.volume_slider = VolumeSlider(center_x=WIDTH // 2, center_y=HEIGHT // 2 + 90)

        self.losepage_img = pygame.image.load('src/assets/interface/lose_page/lose_menu.png').convert_alpha()
        self.losepage_img = pygame.transform.scale(self.losepage_img, (WIDTH, HEIGHT))

        self.winpage_img = pygame.image.load('src/assets/interface/win_page/win_menu.png').convert_alpha()
        self.winpage_img = pygame.transform.scale(self.winpage_img, (WIDTH, HEIGHT))

        self.again_btn_img = pygame.image.load('src/assets/interface/again_button/again_button.png').convert_alpha()
        self.again_btn_rect = self.again_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 78))

        self.exit_btn_img = pygame.image.load('src/assets/interface/exit_button/exit_button.png').convert_alpha()
        self.exit_btn_rect = self.exit_btn_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 125))

    def play_death_animation(self):
        self.sound_manager.stop_sound("ghosts_normal_move")
        self.sound_manager.stop_sound("ghosts_return_to_house")
        self.sound_manager.play_sound("pacman_death")

        for frame in self.player.animations["death"]:
            for event in pygame.event.get():
                self.volume_slider.handle_event(event)

                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.screen.fill(BLACK)
            self.game_map.draw_map(self.screen)

            for ghost in self.ghosts_group:
                ghost.base_speed = self.ghost_speed
                ghost.speed = self.ghost_speed
                self.screen.blit(ghost.image, ghost.rect.move(0, MAP_OFFSET_Y))

            shifted_rect = self.player.rect.move(0, MAP_OFFSET_Y)
            self.screen.blit(frame, shifted_rect)
            pygame.display.flip()

            self.clock.tick(7)

    def draw_score(self):
        score_text = self.font.render(str(self.player.score), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, MAP_OFFSET_Y // 2))
        self.screen.blit(score_text, score_rect)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                self.volume_slider.handle_event(event)

                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
                    self.sound_manager.set_volume(self.volume_slider.get_volume())

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and self.game_state == "game" and not self.escape_pressed:
                        self.sound_manager.play_sound("game_select_button")
                        self.paused = not self.paused
                        self.escape_pressed = True
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        self.escape_pressed = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.game_state == "menu":
                        if self.play_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")
                            self.sound_manager.stop_sound("pacman_menu_theme")

                            self.init_game()
                            self.game_state = "game"
                        if self.menu_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.game_state = "settings"
                    elif self.game_state == "settings":
                        if self.arrow_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.game_state = "menu"
                        if self.easy_mode_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.ghost_speed = 0.8
                            self.game_state = "menu"
                        if self.medium_mode_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.ghost_speed = 1.4
                            self.game_state = "menu"
                        if self.hard_mode_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.ghost_speed = 2.0
                            self.game_state = "menu"
                    elif self.game_state in ("win", "lose"):
                        if self.again_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")
                            self.init_game()
                            self.game_state = "game"
                        elif self.exit_btn_rect.collidepoint(event.pos):
                            self.sound_manager.stop_all_sounds()
                            self.sound_manager.play_sound("game_select_button")
                            self.game_state = "menu"

                    elif self.game_state == "game":
                        if self.pause_btn_rect.collidepoint(event.pos):
                            self.sound_manager.play_sound("game_select_button")

                            self.paused = not self.paused
                        if self.paused:
                            self.sound_manager.stop_all_sounds()

                            result = self.pause_menu.handle_event(event)
                            if result == 'continue':
                                self.sound_manager.play_sound("game_select_button")

                                self.paused = False
                            elif result == 'exit':
                                self.sound_manager.play_sound("game_select_button")

                                self.game_state = "menu"
                                self.paused = False

            if self.game_state == "menu":
                self.sound_manager.play_sound_if_idle("pacman_menu_theme", loops = -1)

                self.screen.blit(self.startpage_img, (0, 0))
                self.screen.blit(self.play_btn_img, self.play_btn_rect)
                self.screen.blit(self.menu_btn_img, self.menu_btn_rect)

            elif self.game_state == "settings":
                self.screen.fill(BLACK)
                self.screen.blit(self.easy_mode_btn_img, self.easy_mode_btn_rect)
                self.screen.blit(self.medium_mode_btn_img, self.medium_mode_btn_rect)
                self.screen.blit(self.hard_mode_btn_img, self.hard_mode_btn_rect)
                self.screen.blit(self.arrow_btn_img, self.arrow_btn_rect)
                self.volume_slider.draw(self.screen)

            elif self.game_state == "win":
                self.screen.blit(self.winpage_img, (0, 0))
                self.screen.blit(self.again_btn_img, self.again_btn_rect)
                self.screen.blit(self.exit_btn_img, self.exit_btn_rect)

            elif self.game_state == "lose":
                self.screen.blit(self.losepage_img, (0, 0))
                self.screen.blit(self.again_btn_img, self.again_btn_rect)
                self.screen.blit(self.exit_btn_img, self.exit_btn_rect)

            elif self.game_state == "game":
                if not self.paused:
                    self.player.update()
                    self.ghosts_group.update()
                    self.objects.update_boost()
                    self.objects.update_objects(self.player)

                    any_ghost_dead = any(ghost.is_dead for ghost in self.ghosts_group)

                    for ghost in self.ghosts_group:
                        ghost.is_scared = self.player.shielded

                    if self.player.shielded:
                        self.sound_manager.stop_sound("ghosts_normal_move")
                        self.sound_manager.stop_sound("ghosts_return_to_house")
                        self.sound_manager.play_sound_if_idle("ghosts_turn_to_blue", loops = -1)
                    elif not any_ghost_dead:
                        self.sound_manager.stop_sound("ghosts_turn_to_blue")
                        self.sound_manager.stop_sound("ghosts_return_to_house")
                        self.sound_manager.play_sound_if_idle("ghosts_normal_move", loops = -1)
                    else:
                        self.sound_manager.stop_sound("ghosts_turn_to_blue")
                        self.sound_manager.stop_sound("ghosts_normal_move")
                        self.sound_manager.play_sound_if_idle("ghosts_return_to_house", loops = -1)

                    collision = pygame.sprite.spritecollide(self.player, self.ghosts_group, False)
                    real_collision = []

                    for i in range(len(collision)):
                        if collision[i].is_dead != True:
                            real_collision = [collision[i]]
                            
                    if real_collision:
                        if self.player.shielded:
                            real_collision[0].is_scared = False
                            real_collision[0].is_dead = True
                            real_collision.pop()

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
                                entity.reset_position(self.player)
                                for ghost in self.ghosts_group:
                                    ghost.spawn_time = pygame.time.get_ticks()
                                    ghost.is_dead = False
                                    ghost.is_scared = False
                                    ghost.path = []
                                    entity.reset_position(ghost)

                    if all(pellet.eaten for pellet in self.objects.pellets):
                        self.sound_manager.stop_all_sounds()
                        self.sound_manager.play_sound_if_idle("pacman_win")
                        self.game_state = "win"

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

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()