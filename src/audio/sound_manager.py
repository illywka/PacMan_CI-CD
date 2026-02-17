import pygame

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        try:
            self.sounds['pacman_death'] = pygame.mixer.Sound('src/assets/sounds/pacman_death.mp3')
            self.sounds['pacman_win'] = pygame.mixer.Sound('src/assets/sounds/pacman_win.mp3')
            self.sounds['pacman_eat_dots'] = pygame.mixer.Sound('src/assets/sounds/pacman_eat_dots.mp3')
            self.sounds['pacman_eat_fruit'] = pygame.mixer.Sound('src/assets/sounds/pacman_eat_fruit.mp3')
        except FileNotFoundError as e:
            print(f"Error loading sound: {e}")

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()