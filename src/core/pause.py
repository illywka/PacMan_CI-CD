import pygame
from src.utils.constants import BLACK, WIDTH, HEIGHT


class Pause:
    """
    In-game pause menu overlay.

    Renders a full-screen black overlay with a "Return" button to resume
    the game and an "Exit" button to return to the main menu. Also
    displays the shared VolumeSlider so the player can adjust audio
    while paused.

    Attributes:
        volume_slider (VolumeSlider): Shared slider instance passed in
            from the main Game class.
        return_btn_img (pygame.Surface): Image for the continue/return button.
        exit_btn_img (pygame.Surface): Image for the exit-to-menu button.
        return_btn_rect (pygame.Rect): Bounding rect for the return button,
            centred slightly above screen centre.
        exit_btn_rect (pygame.Rect): Bounding rect for the exit button,
            centred slightly below screen centre.
    """
    def __init__(self, volume_slider):
        """
        Initialise the pause menu with a shared volume slider.

        Args:
            volume_slider (VolumeSlider): The volume slider instance shared
                with the main Game class, so slider state persists across
                paused and unpaused sessions.

        Returns:
            None
        """
        self.volume_slider = volume_slider
        self.load_assets()
        self.setup_buttons()

    def load_assets(self):
        """
        Load button images from dir and convert them for fast blitting.

        Args:
            None

        Returns:
            None
        """
        self.return_btn_img = pygame.image.load(
            'src/assets/interface/return_button/return_button.png'
        ).convert_alpha()

        self.exit_btn_img = pygame.image.load(
            'src/assets/interface/exit_button/exit_button.png'
        ).convert_alpha()

    def setup_buttons(self):
        """
        Position button rects relative to the screen centre.

        The return button is placed 30 pixels above centre and the exit
        button 30 pixels below, so the two buttons sit symmetrically
        around the midpoint of the screen.

        Args:
            None

        Returns:
            None
        """
        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        self.return_btn_rect = self.return_btn_img.get_rect(
            center=(center_x, center_y - 30))
        self.exit_btn_rect = self.exit_btn_img.get_rect(
            center=(center_x, center_y + 30))

    def handle_event(self, event) -> str | None:
        """
        Process a single Pygame event and return an action string if a
        button was clicked.

        Forwards every event to the volume slider first, then checks for
        MOUSEBUTTONDOWN collisions with the pause menu buttons.

        Args:
            event (pygame.event.Event): A Pygame event object, typically
                obtained from the main event loop via pygame.event.get().

        Returns:
            str | None:
                - ``'continue'`` if the return button was clicked.
                - ``'exit'``     if the exit button was clicked.
                - ``None``       for all other events.
        """
        self.volume_slider.handle_event(event)
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if self.return_btn_rect.collidepoint(pos):
                return 'continue'

            if self.exit_btn_rect.collidepoint(pos):
                return 'exit'

        return None

    def draw(self, screen):
        """
        Draw the pause overlay onto the given surface.

        Fills the entire surface with black, then blits the return and exit
        buttons at their pre-calculated rects, and finally draws the volume
        slider on top.

        Args:
            screen (pygame.Surface): The surface to draw onto, typically
                the main display surface passed from the Game class.

        Returns:
            None
        """
        screen.fill(BLACK)

        screen.blit(self.return_btn_img, self.return_btn_rect)
        screen.blit(self.exit_btn_img, self.exit_btn_rect)
        self.volume_slider.draw(screen)
