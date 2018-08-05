import pygame.locals

from ecs.systems.system import System
from ecs.components.component import *

SPEED = 4

class UserInputSystem(System):
    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        for key, entity in game.entities.items():
            # Can a player control an object that has a position
            if PlayerControl in entity and IngameObject in entity:
                playercontrol = entity[PlayerControl]
                # Is the player that can control it them?
                if game.net.is_me(playercontrol.player_id):
                    io = entity[IngameObject]
                    moved = False
                    direction = entity[Directioned].direction if Directioned in entity else 'default'
                    if keysdown[pygame.locals.K_DOWN]:
                        io.position = (io.position[0], io.position[1] + SPEED)
                        moved = True
                        direction = 'down'
                    elif keysdown[pygame.locals.K_UP]:
                        io.position = (io.position[0], io.position[1] - SPEED)
                        moved = True
                        direction = 'up'
                    elif keysdown[pygame.locals.K_LEFT]:
                        io.position = (io.position[0] - SPEED, io.position[1])
                        moved = True
                        direction = 'left'
                    elif keysdown[pygame.locals.K_RIGHT]:
                        io.position = (io.position[0] + SPEED, io.position[1])
                        moved = True
                        direction = 'right'
                    # Animate their sprite, if we should
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = moved
                    if Directioned in entity:
                        entity[Directioned].direction = direction
