import pygame
from enum import Enum

class Sprite():
    def __init__(self, screen, map, image):
        self.screen = screen
        self.map = map
        self.image = pygame.image.load(image)

        self.x, self.y = (0, 0)
        self.animation_ticker = 0
    
    def set_position(self, position):
        self.x, self.y = position

    def render(self):
        centre = self.map.get_pixel_pos(self.x, self.y)
        self.screen.blit(self.image, centre)
        # create collision rectangle
        self.rect = self.image.get_rect()
        self.rect.topleft = centre
