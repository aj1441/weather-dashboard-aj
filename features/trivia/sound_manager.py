# trivia/sound_manager.py

import pygame
import os

class SoundManager:
    def __init__(self, base_path="assets"):
        pygame.mixer.init()
        self.sounds = {
            "right": self._load_sound(base_path, "right.wav"),
            "wrong": self._load_sound(base_path, "wrong.wav"),
            "round_over": self._load_sound(base_path, "round_over.wav"),
            "thunder": self._load_sound(base_path, "thunder.wav"),
        }

    def _load_sound(self, base_path, filename):
        path = os.path.join(base_path, filename)
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
        else:
            print(f"Warning: Sound file '{filename}' not found.")
            return None

    def play(self, sound_key):
        sound = self.sounds.get(sound_key)
        if sound:
            sound.play()

# Usage:
# sound_mgr = SoundManager()
# sound_mgr.play("right")