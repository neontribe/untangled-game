import sys
import uuid

from next.ecs.systems.eventsystem import EventSystem
from next.ecs.systems.rendersystem import RenderSystem
from next.ecs.systems.userinputsystem import UserInputSystem
from next.ecs.components.component import *

class Game:
    fps = 60
    running = True
    clock = pygame.time.Clock()
    entities = {}
    systems = []

    def __init__(self):

        self.systems.extend([
            RenderSystem(),
            EventSystem(),
            UserInputSystem()
        ])

        test_surface = pygame.Surface((100, 100))
        test_surface.fill((255,255,255))

        self.add_entity([
            RenderComponent(test_surface),
            KeyboardComponent(),
            PlayerControlComponent(),
        ])

    def add_entity(self, components: list):
        uuid_def = uuid.uuid4()
        self.entities[uuid_def] = {type(value): value for (value) in components}
        return uuid_def

    def main_loop(self):
        dt = 0
        self.clock.tick(self.fps)
        while self.running:
            for s in self.systems:
                s.update(self, dt)

            dt = self.clock.tick(self.fps)/1000.0


def main():
    game = Game()
    game.main_loop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
