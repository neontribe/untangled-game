import pygame.locals

from lib.system import System
from game.systems.mapsystem import MapSystem
from game.components import *
import math
import time
from game.systems.particlesystem import Particle

SPEED = 150

class UserInputSystem(System):
    """This system updates certain entities based on the arrow keys."""

    debug = {}

    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        map = None
        for key, entity in game.entities.items():
            if Map in entity:
                map = entity

        #print(dt)
        for key, entity in game.entities.items():
            # Is the object player controllable and does it have a position on-screen?
            if PlayerControl in entity and IngameObject in entity:
                # Is the player that can control it us?
                if game.net.is_me(entity[PlayerControl].player_id):
                    # Our ingane position and size
                    io = entity[IngameObject]

                    prePos = io.position

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
                    
                    
                    if keysdown[pygame.locals.K_LEFT]:
                        vel.x = -SPEED * dt
                        moved = True
                        direction = 'left'
                    elif keysdown[pygame.locals.K_RIGHT]:
                        vel.x = SPEED * dt
                        moved = True
                        direction = 'right'

                    grid = map[Map].grid


                    player_width = 64
                    tile_width = 32

                    pos_applied_vel = temp_position + vel
                    player_center = ((pos_applied_vel.x + (player_width/2)), (pos_applied_vel.y + (player_width/2)))
                    current_tile = (
                        round(player_center[0] / tile_width) - 1,
                        round(player_center[1] / tile_width) - 1
                    )


                    game.renderSystem.debugPoints.append(([player_center[0] - vel.x, player_center[1] - vel.y],(0,255,0)))
                    game.renderSystem.debugPoints.append((player_center,(0,0,255)))
                    game.renderSystem.debugPoints.append((pos_applied_vel,(255,255,255)))

                    
                    points = [
                        [-0.45,-0.45],[0,-1],[0.45,-0.45], # 0 1 2
                        [-1,0],[0,0],[1,0],            # 3 4 5
                        [-0.45,0.45],[0,1],[0.45,0.45]     # 6 7 8
                    ]
                    left = [0,3,6]
                    right = [2,5,8]
                    up = [0,1,2]
                    down = [6,7,8]

                    non_col_tiles = [1, 15]

                    for tile in MapSystem.get_surrounding_blocks(grid, current_tile,keysdown[pygame.locals.K_SPACE],self.debug):
                        x, y, t = tile
                        x *= tile_width
                        y *= tile_width

                        if t in non_col_tiles: #what's non collidable?
                            continue

                        tile_center = ( (x + (tile_width/2)), (y + (tile_width/2)) )
                        sameX = abs(player_center[0] - tile_center[0]) < player_width
                        sameY = abs(player_center[1] - tile_center[1]) < player_width

                        for i, pOff in enumerate(points):
                            offset = (tile_width * pOff[0], tile_width * pOff[1]) 
                            point = (player_center[0] + offset[0], player_center[1] + offset[1])
                            if x <= point[0] and point[0] <= x + tile_width:
                                if y <= point[1] and point[1] <= y + tile_width:
                                    #SHOULD COLLIDE
                                    game.renderSystem.debugPoints.append((point,(255,0,0)))
                                    if vel.x > 0 and i in right: # right
                                        if pos_applied_vel.x + player_width > tile_center[0]:
                                            pos_applied_vel.x = tile_center[0] - player_width + 1
                                    elif vel.x < 0 and i in left: # left
                                        if pos_applied_vel.x < tile_center[0]:
                                            pos_applied_vel.x = tile_center[0]

                                    if vel.y > 0 and i in down: # down
                                        if pos_applied_vel.y + player_width > tile_center[1]:
                                            pos_applied_vel.y = tile_center[1] - player_width + 1
                                    elif vel.y < 0 and i in up: # up
                                        if pos_applied_vel.y < tile_center[1]:
                                            pos_applied_vel.y = tile_center[1]
                                        


                    io.position = (pos_applied_vel.x,pos_applied_vel.y)



                    # Trigger animation of this entity's sprite, if it has one
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = moved
                    if Directioned in entity:
                        entity[Directioned].direction = direction