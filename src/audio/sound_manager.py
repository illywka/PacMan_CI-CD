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
            self.sounds['ghosts_normal_move'] = pygame.mixer.Sound('src/assets/sounds/ghosts_normal_move.mp3')
            self.sounds['pacman_eat_fruit'] = pygame.mixer.Sound('src/assets/sounds/pacman_eat_fruit.mp3')
        except FileNotFoundError as e:
            print(f"Error loading sound: {e}")

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def stop_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
    def play_sound_if_idle(self, sound_name):
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            if sound.get_num_channels() == 0:
                sound.play()