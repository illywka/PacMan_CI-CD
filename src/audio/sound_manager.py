import pygame

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        try:
            self.sounds['sound_1'] = pygame.mixer.Sound('sounds/sound_1.wav')
        except FileNotFoundError as e:
            print(f"Error loading sound: {e}")

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()