import pygame

from next.ecs.systems.system import System
from next.ecs.components.component import *


class RenderSystem(System):
    def __init__(self, width: int = 1024, height: int = 1024, caption: str = 'Untangled 2018'):
        super().__init__()
        pygame.init()
        pygame.display.set_caption(caption)
        pygame.display.set_mode((width, height))
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)

    def update(self, entities: dict, dt: float=0):
        self.screen.fill((0,0,0))

        for key, entity in entities.items():
            if RenderComponent in entity:
                render_component: RenderComponent = entity[RenderComponent]

                testrectangle = pygame.Surface((100,100))
                testrectangle.fill((255,255,255))
                self.screen.blit(testrectangle, render_component.coordinates)

        pygame.display.update()
