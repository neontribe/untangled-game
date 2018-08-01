import pygame.locals

from next.ecs.systems.system import System
from next.ecs.components.component import *


class UserInputSystem(System):
    def update(self, game, dt: float = 0.0):
        for key, entity in game.entities.items():
            if self.check_components(entity, (KeyboardComponent, PlayerControlComponent, RenderComponent)):
                keyboard_component: KeyboardComponent = entity[KeyboardComponent]
                render_component: RenderComponent = entity[RenderComponent]
                playercontrol_component = entity[PlayerControlComponent]

                if keyboard_component.keys[pygame.locals.K_DOWN]:
                    render_component.coordinates += (0, 1)
                elif keyboard_component.keys[pygame.locals.K_UP]:
                    render_component.coordinates += (0, -1)

                if keyboard_component.keys[pygame.locals.K_LEFT]:
                    render_component.coordinates += (-1, 0)
                elif keyboard_component.keys[pygame.locals.K_RIGHT]:
                    render_component.coordinates += (1, 0)



