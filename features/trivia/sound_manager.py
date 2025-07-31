# trivia/sound_manager.py

import os
import logging

logger = logging.getLogger(__name__)

# Global variable for pygame availability
PYGAME_AVAILABLE = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    logger.warning("pygame not available - sound features will be disabled")

class SoundManager:
    def __init__(self, base_path="assets"):
        global PYGAME_AVAILABLE
        self.sounds = {}
        if PYGAME_AVAILABLE:
            try:
                # More defensive pygame initialization
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                logger.info("pygame mixer initialized successfully")
                
                self.sounds = {
                    "right": self._load_sound(base_path, "right.wav"),
                    "wrong": self._load_sound(base_path, "wrong.wav"),
                    "round_over": self._load_sound(base_path, "round_over.wav"),
                    "thunder": self._load_sound(base_path, "thunder.wav"),
                }
                logger.info(f"Loaded {len([s for s in self.sounds.values() if s])} sound files")
            except Exception as e:
                logger.error(f"Failed to initialize pygame mixer: {e}")
                PYGAME_AVAILABLE = False
                self.sounds = {}

    def _load_sound(self, base_path, filename):
        if not PYGAME_AVAILABLE:
            return None
            
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            try:
                return pygame.mixer.Sound(path)
            except Exception as e:
                logger.error(f"Failed to load sound {filename}: {e}")
                return None
        else:
            logger.warning(f"Sound file '{filename}' not found at {path}")
            return None

    def play(self, sound_key):
        if not PYGAME_AVAILABLE:
            return
            
        sound = self.sounds.get(sound_key)
        if sound:
            try:
                sound.play()
            except Exception as e:
                logger.error(f"Failed to play sound {sound_key}: {e}")

# Usage:
# sound_mgr = SoundManager()
# sound_mgr.play("right")