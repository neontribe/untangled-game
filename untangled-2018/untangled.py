import sys
import uuid
import pygame

from typing import List

from ecs.menu import MenuState, MenuStates
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
        pygame.font.init()
        pygame.display.set_caption(self.caption)
        self.screen = pygame.display.set_mode(self.dimensions, pygame.HWSURFACE | pygame.DOUBLEBUF)

        self.net = Network()

        import time
        time.sleep(1)

        if len(self.net.get_all_groups()) == 0:
            self.net.host_group('test')
        else:
            self.net.join_group(self.net.get_all_groups()[0])

        self.state = GameState(self)
        self.menu = MenuState(self)

    def main_loop(self):
        self.clock.tick()
        while self.running:
            self.screen.fill((0, 0, 0))
            dt = self.clock.tick(self.fps) / 1000.0

            if self.menu.current_state == MenuStates.QUIT:
                self.running = False

            if self.menu.current_state != MenuStates.PLAY:
                self.menu.update(dt)
                self.menu.render()
            else:
                self.state.update(dt)

            pygame.display.update()

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

        if self.net.is_hosting():
            self.add_entity([
                RenderComponent(x=0, y=0, width=10, height=10, color='white'),
                KeyboardComponent(),
                PlayerControlComponent(),
            ])

    def add_entity(self, components: List[dataclass]) -> uuid.UUID:
        key = uuid.uuid4()
        self.entities[key] = {type(value): value for (value) in components}
        return key

    def on_player_join(self, uuid):
        pass

    def on_player_quit(self, uuid):
        pass

    def update(self, dt: float) -> None:
        self.net.pull_game(self)

        # local update
        for system in self.systems:
            system.update(self, dt)

        self.net.push_game(self)

if __name__ == "__main__":
    app = Framework()
    app.main_loop()
