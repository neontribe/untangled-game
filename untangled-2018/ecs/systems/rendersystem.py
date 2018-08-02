from ecs.systems.system import System
from ecs.components.component import *


class RenderSystem(System):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

    def update(self, game, dt: float=0.0):
        self.screen.fill((0,0,0))

        for key, entity in game.entities.items():
            if RenderComponent in entity:
                render_component: RenderComponent = entity[RenderComponent]
                self.screen.blit(render_component.surface, render_component.coordinates)

        pygame.display.update()

