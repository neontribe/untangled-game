from ecs.systems.system import System
from ecs.components.component import *

import pygame

class RenderSystem(System):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def update(self, game, dt: float=0.0):
        for key, entity in game.entities.items():
            if RenderComponent in entity:
                render_component: RenderComponent = entity[RenderComponent]
                self.screen.blit(render_component.surface, render_component.coordinates)
                pygame.draw.rect(self.screen, pygame.Color(render_component.color), pygame.Rect(render_component.x, render_component.y, render_component.width, render_component.height))
