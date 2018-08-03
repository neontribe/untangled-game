import pygame.locals

from ecs.systems.system import System
from ecs.components.component import *


class UserInputSystem(System):
    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        for key, entity in game.entities.items():
            if self.check_components(entity, (PlayerControlComponent, RenderComponent)):
                playercontrol = entity[PlayerControlComponent]
                if game.net.is_me(playercontrol.player_id):
                    render: RenderComponent = entity[RenderComponent]
                    if keysdown[pygame.locals.K_DOWN]:
                        render.y += 1
                    if keysdown[pygame.locals.K_UP]:
                        render.y -= 1
                    if keysdown[pygame.locals.K_LEFT]:
                        render.x -= 1
                    if keysdown[pygame.locals.K_RIGHT]:
                        render.x += 1
