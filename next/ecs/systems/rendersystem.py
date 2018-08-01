from next.ecs.systems.system import System
from next.ecs.components.component import *


class RenderSystem(System):
    def __init__(self, width: int = 1024, height: int = 1024, caption: str = 'Untangled 2018'):
        pygame.init()
        pygame.display.set_caption(caption)
        pygame.display.set_mode((width, height))
        self.screen = pygame.display.set_mode((width, height), pygame.HWSURFACE | pygame.DOUBLEBUF)

    def update(self, game, dt: float=0.0):
        self.screen.fill((0,0,0))

        for key, entity in game.entities.items():
            if RenderComponent in entity:
                render_component: RenderComponent = entity[RenderComponent]
                self.screen.blit(render_component.surface, render_component.coordinates)

        pygame.display.update()

