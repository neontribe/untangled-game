import pygame
from dataclasses import dataclass


@dataclass
class KeyboardComponent:
        keys: tuple = ()


@dataclass
class RenderComponent:
        surface: pygame.Surface
        coordinates: pygame.Vector2


@dataclass
class PlayerControlComponent:
    player_controlled: bool = True
