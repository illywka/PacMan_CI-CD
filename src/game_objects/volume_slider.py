import pygame

class VolumeSlider:
    """
    An interactive horizontal slider for controlling music volume.

    Renders a three-layer composite: a static background bar, a fill strip
    that grows from the left edge to the knob position, and a draggable knob.
    Dragging the knob updates the volume in real time via pygame.mixer.

    Attributes:
        bar_img (pygame.Surface): Background bar sprite.
        fill_img (pygame.Surface): Full-width fill sprite, cropped each frame
            to represent the current volume level.
        knob_img (pygame.Surface): Draggable knob sprite.
        bar_rect (pygame.Rect): Bounding rect of the background bar,
            centred on the construction coordinates.
        fill_rect (pygame.Rect): Rect of the fill strip; its left edge is
            pinned to the bar's left edge and its width tracks the knob.
        knob_rect (pygame.Rect): Bounding rect of the knob; its centerx is
            repositioned by _update_knob_pos() on every change.
        min_x (int): Pixel x coordinate the knob centre can not go left of,
            inset by half the knob width from the bar's left edge.
        max_x (int): Pixel x coordinate the knob centre can not go right of,
            inset by half the knob width from the bar's right edge.
        volume (float): Current volume in the range [0.0, 1.0].
        dragging (bool): True while the user is holding the knob.
    """
    def __init__(self, center_x: int, center_y: int):
        """
        Load slider assets, position all rects, and set the default volume.

        All three sprite rects are initially centred on (center_x, center_y).
        _update_knob_pos() is called immediately to align the knob and fill
        strip with the default volume of 0.5.

        Args:
            center_x (int): Pixel x coordinate for the centre of the slider.
            center_y (int): Pixel y coordinate for the centre of the slider.

        Returns:
            None
        """
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
        """
        Reposition the knob and resize the fill strip to match self.volume.

        Maps the normalised volume value to a pixel x coordinate between
        min_x and max_x, moves knob_rect.centerx to that position, then
        sets fill_rect to span from the bar's left edge to the knob centre.

        Args:
            None

        Returns:
            None
        """
        x = self.min_x + int(self.volume * (self.max_x - self.min_x))
        self.knob_rect.centerx = x
        self.knob_rect.centery = self.bar_rect.centery

        self.fill_rect.left = self.bar_rect.left
        self.fill_rect.width = x - self.bar_rect.left

    def handle_event(self, event: pygame.event.Event):
        """
        Process a Pygame event and update drag state or volume accordingly.

        MOUSEBUTTONDOWN on the knob begins dragging. MOUSEBUTTONUP ends it.
        During MOUSEMOTION while dragging, the knob is clamped to [min_x,
        max_x], volume is recalculated, knob and fill are repositioned, and
        pygame.mixer.music.set_volume() is called immediately.

        Args:
            event (pygame.event.Event): A Pygame event from the main loop.

        Returns:
            None
        """
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

    def draw(self, screen: pygame.Surface):
        """
        Blit the bar, fill strip, and knob onto the screen in layer order.

        The bar is drawn first, the fill strip on top, and the knob last so
        it always appears in front.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface.

        Returns:
            None
        """
        screen.blit(self.bar_img, self.bar_rect)
        screen.blit(self.fill_img, self.fill_rect) 
        screen.blit(self.knob_img, self.knob_rect)