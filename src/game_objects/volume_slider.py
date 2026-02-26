import pygame

class VolumeSlider:
    def __init__(self, center_x, center_y):
        self.bar_img = pygame.image.load('src/assets/interface/volume_slider/volume_bar.png').convert_alpha()
        self.fill_img = pygame.image.load('src/assets/interface/volume_slider/volume_full.png').convert_alpha()
        self.knob_img = pygame.image.load('src/assets/interface/volume_slider/volume_knob.png').convert_alpha()

        self.bar_rect = self.bar_img.get_rect(center=(center_x, center_y))
        self.fill_rect = self.fill_img.get_rect(center=(center_x, center_y))
        self.knob_rect = self.knob_img.get_rect(center=(center_x, center_y))

        self.min_x = self.bar_rect.left + self.knob_rect.width // 2
        self.max_x = self.bar_rect.right - self.knob_rect.width // 2

        self.volume = 0.5
        self.dragging = False

        self._update_knob_pos()

    def _update_knob_pos(self):
        x = self.min_x + int(self.volume * (self.max_x - self.min_x))
        self.knob_rect.centerx = x
        self.knob_rect.centery = self.bar_rect.centery

        self.fill_rect.left = self.bar_rect.left
        self.fill_rect.width = x - self.bar_rect.left

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos):
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                x = max(self.min_x, min(event.pos[0], self.max_x))
                self.volume = (x - self.min_x) / (self.max_x - self.min_x)
                self._update_knob_pos()
                pygame.mixer.music.set_volume(self.volume)

    def draw(self, screen):
        screen.blit(self.bar_img, self.bar_rect)
        screen.blit(self.fill_img, self.fill_rect) 
        screen.blit(self.knob_img, self.knob_rect)

    def get_volume(self):
        return self.volume