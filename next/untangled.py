import pygame
import sys, uuid

from next.ecs.systems.rendersystem import RenderSystem
from next.ecs.components.component import RenderComponent

game = None


class Game:
    fps = 60
    running = True
    clock = pygame.time.Clock()
    entities = {}
    systems = []

    def __init__(self):
        self.systems.append(RenderSystem())
        self.add_entity([RenderComponent()])

    def add_entity(self, components: list):
        uuid_def = uuid.uuid4()
        self.entities[uuid_def] = {type(value): value for (value) in components}
        return uuid_def

    def event_loop(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                self.keys = pygame.key.get_pressed()

    def main_loop(self):
        dt = 0
        self.clock.tick(self.fps)
        while self.running:
            self.event_loop()
            for s in self.systems:
                s.update(self.entities, dt)
            dt = self.clock.tick(self.fps)/1000.0


def main():
    game = Game()
    game.main_loop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
