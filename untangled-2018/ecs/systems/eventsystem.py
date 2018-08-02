from ecs.systems.system import System
from ecs.components.component import *


class EventSystem(System):
    def update(self, game, dt: float = 0.0):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.framework.running = False

        for key, entity in game.entities.items():
            if KeyboardComponent in entity:
                keyboard_component: KeyboardComponent = entity[KeyboardComponent]
                keyboard_component.keys = pygame.key.get_pressed()
