import sys
import uuid
import pygame

from typing import List
from ecs.network import Network
from ecs.systems.eventsystem import EventSystem
from ecs.systems.rendersystem import RenderSystem
from ecs.systems.userinputsystem import UserInputSystem
from ecs.components.component import *


class Framework:
    caption = 'Untangled 2018'
    dimensions = (1024, 1024)
    fps = 60
    running = True
    clock = pygame.time.Clock()

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.dimensions, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.net = Network()

        if len(self.net.get_groups()) == 0:
            self.net.host_group('test')
        else:
            self.net.join_group(self.net.get_groups()[0])

        self.state = GameState(self)

    def main_loop(self):
        self.clock.tick()
        while self.running:
            dt = self.clock.tick(self.fps) / 1000.0
            self.state.update(dt)

        pygame.quit()
        self.net.close()
        sys.exit()


class GameState:
    entities = {}
    systems = []

    def __init__(self, framework: Framework):
        self.framework = framework
        self.screen = framework.screen
        self.net = framework.net

        self.systems.extend([
            EventSystem(),
            UserInputSystem(),
            RenderSystem(self.screen)
        ])

        test_surface = pygame.Surface((100, 100))
        test_surface.fill((255, 255, 255))

        self.add_entity([
            RenderComponent(test_surface, pygame.Vector2()),
            KeyboardComponent(),
            PlayerControlComponent(),
        ])

    def add_entity(self, components: List[dataclass]) -> uuid.UUID:
        uuid_def = uuid.uuid4()
        self.entities[uuid_def] = {type(value): value for (value) in components}
        return uuid_def

    def update(self, dt: float) -> None:
        for system in self.systems:
            system.update(self, dt)


if __name__ == "__main__":
    app = Framework()
    app.main_loop()

