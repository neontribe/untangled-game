import pygame.locals

from lib.system import System
from game.components import *

SPEED = 4

class UserInputSystem(System):
    """This system updates certain entities based on the arrow keys."""

    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        mousedown = pygame.mouse.get_pressed()

        for key, entity in game.entities.items():
            # Is the object player controllable and does it have a position on-screen?
            if PlayerControl in entity and IngameObject in entity:
                # Is the player that can control it us?
                if game.net.is_me(entity[PlayerControl].player_id):
                    # Our ingane position and size
                    io = entity[IngameObject]

                    # Store whether we've moved this frame
                    moved = False

                    # Store which direction we moved in
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

                    # Trigger animation of this entity's sprite, if it has one
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = moved
                    if Directioned in entity:
                        entity[Directioned].direction = direction

                    # Checks if mouse is pressed
                    if mousedown:
                        mouse_x, mouse_y = pygame.mouse.get_pos()