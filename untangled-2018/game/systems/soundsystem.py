from lib.system import System
from game.components import *
import pygame

class SoundSystem(System):
    def __init__(self):
        self.playingMusic = ""
    def update(self, game, dt, events):
        for key,entity in game.entities.items():
            if BackgroundMusic in entity:
                path = entity[BackgroundMusic].path
                if self.playingMusic != path:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                    self.playingMusic = path
                elif not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play()
