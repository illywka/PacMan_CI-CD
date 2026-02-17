import random
import time
import pygame
from collections import deque
from src.game_objects.pellet import Pellet
from src.game_objects.boost import CakeBoost, StrawberryBoost, WatermelonBoost
from src.utils.constants import TILE_SIZE

class ObjectManager:
    def __init__(self, game_map):
        self.map = game_map
        self.pellets = []
        self.boosts = []
        self.current_boost = None
        self.last_boost_time = 0
        self.boost_interval = 10
        self.last_pellet_sfx_time = 0
        self.pellet_sfx_cooldown = 0.2

    def is_walkable(self, x, y):
        return self.map.level[y][x] == 0

    def is_ghost_zone(self, x, y):
        return(self.map.ghost_start_x <= x < self.map.ghost_start_x + 3 and 
               self.map.ghost_start_y <= y < self.map.ghost_start_y + 3)

    def find_reachable_tiles(self, start_x, start_y):
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

    def get_valid_tiles(self, start_x = 1, start_y = 1):
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
        valid_tiles = self.get_valid_tiles()
        self.pellets = [Pellet(x, y) for x, y in valid_tiles]

        if player:
            for pellet in self.pellets:
                if player.rect.colliderect(pellet.rect):
                    pellet.eaten = True

    def spawn_boost(self):
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
        current_time = time.time()
        if current_time - self.last_boost_time >= self.boost_interval:
            self.current_boost = None
            self.spawn_boost()
            self.last_boost_time = current_time

    def draw_objects(self, screen):
        for pellet in self.pellets:
            if not pellet.eaten: 
                pellet.draw(screen)
        if self.current_boost:
            self.current_boost.draw(screen)
    
    def update_objects(self, player):
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