import pygame
from src.utils.constants import TILE_SIZE, PACMAN_SPEED, WIDTH
from src.audio.sound_manager import SoundManager
import src.entities.entity as entity
import time

class Pacman(pygame.sprite.Sprite):
    def __init__(self, x, y, game_map):
        super().__init__()
        self.sound_manager = SoundManager()
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
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft = (self.start_pos.x, self.start_pos.y))
    
    def update_boost(self):
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
        self.get_input()
        self.move()
        self.animate()
        self.update_boost()