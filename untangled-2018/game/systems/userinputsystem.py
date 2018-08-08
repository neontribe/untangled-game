import pygame.locals

from lib.system import System
from game.systems.mapsystem import MapSystem
from game.components import *

SPEED = 150

class UserInputSystem(System):
    """This system updates certain entities based on the arrow keys."""

    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        map = None
        for key, entity in game.entities.items():
            if Map in entity:
                map = entity


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

                    temp_position = pygame.Vector2(x=io.position[0], y=io.position[1])
                    vel = pygame.Vector2(x=0, y=0)


                    if keysdown[pygame.locals.K_DOWN]:
                        vel.y = SPEED * dt
                        moved = True
                        direction = 'down'
                    elif keysdown[pygame.locals.K_UP]:
                        vel.y = -SPEED * dt
                        moved = True
                        direction = 'up'
                    elif keysdown[pygame.locals.K_LEFT]:
                        vel.x = -SPEED * dt
                        moved = True
                        direction = 'left'
                    elif keysdown[pygame.locals.K_RIGHT]:
                        vel.x = SPEED * dt
                        moved = True
                        direction = 'right'

                    grid = map[Map].grid

                    pos_applied_vel = temp_position + vel

                    for tile in MapSystem.get_surrounding_blocks(grid, (io.position[0]/32, io.position[1]/32), direction):
                        x, y, type = tile
                        x *= 32
                        y *= 32
                        tile_collide = pygame.Rect(x, y, 32, 32)
                        player_collide = pygame.Rect(pos_applied_vel.x, pos_applied_vel.y, 32, 32)

                        if tile_collide.colliderect(player_collide):
                            if vel.x > 0:
                                if player_collide.x > tile_collide.x - 1:
                                    if type != 1:
                                        pos_applied_vel.x = tile_collide.x - 1

                            elif vel.x < 0:
                                if pos_applied_vel.x < tile_collide.x + 32:
                                    if type != 1:
                                        pos_applied_vel.x = tile_collide.x + 32

                            if vel.y > 0:
                                if pos_applied_vel.y > tile_collide.y - 1:
                                    if type != 1:
                                        pos_applied_vel.y = tile_collide.y - 1
                            elif vel.y < 0:
                                if pos_applied_vel.y < tile_collide.y + 32:
                                    if type != 1:
                                        pos_applied_vel.y = tile_collide.y + 32

                    io.position = (pos_applied_vel.x, pos_applied_vel.y)



                    # Trigger animation of this entity's sprite, if it has one
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = moved
                    if Directioned in entity:
                        entity[Directioned].direction = direction
