import pygame
from enum import Enum

class Sprite():
    def __init__(self, screen, map, image):
        self.screen = screen
        self.map = map
        self.image = image
        self.player = None
        self.x, self.y = (0, 0)
        self.animation_ticker = 0
    
    def set_position(self, position):
        self.x, self.y = position

    def set_player(self, player):
        self.player = player

    def render(self):                   
        if self.player:
            self.x, self.y = self.player.x, self.player.y

        centre = self.map.get_pixel_pos(self.x + 0.5, self.y - 0.2)
        self.rect = self.image.get_rect()
        self.rect.center = centre
        self.screen.blit(self.image, self.rect.topleft)
