import pygame


class SoundManager:
    """
    Manages all sound effects and audio playback for the game.

    This class handles loading, playing, stopping, and volume control
    for all game sound effects including Pacman movements, ghost sounds,
    menu interactions, and game events.
    """

    def __init__(self):
        """
        Initialize the sound manager with default volume and load all sounds.

        Args:
            None

        Returns:
            None
        """

        self.current_volume = 0.5
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        """
        Load all game sound effects from the assets folder.

        Loads sound files for Pacman actions (death, eating, winning/losing),
        ghost movements and state changes, and UI interactions (button clicks,
        menu theme). Handles FileNotFoundError if sound files are missing.

        Args:
            None

        Returns:
            None
        """

        try:
            self.sounds['pacman_death'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_death.mp3')
            self.sounds['pacman_win'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_win.mp3')
            self.sounds['pacman_eat_dots'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_eat_dots.mp3')
            self.sounds['ghosts_normal_move'] = pygame.mixer.Sound(
                'src/assets/sounds/ghosts_normal_move.mp3')
            self.sounds['pacman_eat_fruit'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_eat_fruit.mp3')
            self.sounds['game_select_button'] = pygame.mixer.Sound(
                'src/assets/sounds/game_select_button.mp3')
            self.sounds['pacman_menu_theme'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_menu_theme.mp3')
            self.sounds['ghosts_turn_to_blue'] = pygame.mixer.Sound(
                'src/assets/sounds/ghosts_turn_to_blue.mp3')
            self.sounds['ghosts_return_to_house'] = pygame.mixer.Sound(
                'src/assets/sounds/ghosts_return_to_house.mp3')
            self.sounds['pacman_lose'] = pygame.mixer.Sound(
                'src/assets/sounds/pacman_lose.mp3')
        except FileNotFoundError as e:
            print(f"Error loading sound: {e}")

    def play_sound(self, sound_name):
        """
        Play a sound effect once at the current volume level.

        Checks if the sound exists in the loaded sounds dictionary,
        sets its volume to the current global volume, and plays it once.

        Args:
            sound_name (str): The name/key of the sound to play

        Returns:
            None
        """

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.play()

    def stop_sound(self, sound_name):
        """
        Stop a currently playing sound effect.

        If the sound exists in the loaded sounds dictionary,
        stops its playback immediately.

        Args:
            sound_name (str): The name/key of the sound to stop

        Returns:
            None
        """

        if sound_name in self.sounds:
            self.sounds[sound_name].stop()

    def play_sound_if_idle(self, sound_name, loops=0):
        """
        Play a sound only if it's not already playing.

        Useful for background music and looping sounds to prevent
        multiple instances from playing simultaneously. Checks if
        the sound is currently playing on any channel before starting it.

        Args:
            sound_name (str): The name/key of the sound to play
            loops (int): Number of times to loop (-1 for infinite loop)

        Returns:
            None
        """

        if sound_name in self.sounds:
            sound = self.sounds[sound_name]

            if sound.get_num_channels() == 0:
                sound.play(loops=loops)

    def stop_all_sounds(self):
        """
        Stop all currently playing sound effects.

        Iterates through all loaded sounds and stops their playback.
        Useful when transitioning between game states or pausing.

        Args:
            None

        Returns:
            None
        """

        for sound in self.sounds.values():
            sound.stop()

    def set_volume(self, volume):
        """
        Set the volume level for all sounds.

        Updates the current volume level and applies it to the pygame
        mixer and all loaded sound effects. Volume is clamped between
        0.0 (mute) and 1.0 (maximum volume).

        Args:
            volume (float): Volume level between 0.0 (mute) and 1.0 (max)

        Returns:
            None
        """

        self.current_volume = volume
        pygame.mixer.music.set_volume(volume)

        for sound in self.sounds.values():
            sound.set_volume(volume)
