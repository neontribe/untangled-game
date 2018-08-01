import pygame

class KeyboardComponent:
    def __init__(self):
        self.keys = []


class RenderComponent:
    def __init__(self, surface, coordinates=pygame.Vector2()):
        self.coordinates = coordinates
        self.surface = surface

class PlayerControlComponent:
    def __init__(self, player_controlled=True):
        self.player_controlled = player_controlled
