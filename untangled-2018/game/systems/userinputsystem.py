import math
import pygame.locals

from lib.system import System
from game.components import *
from game.systems.particlesystem import Particle

SPEED = 10

class UserInputSystem(System):
    """This system updates certain entities based on the arrow keys."""

    def update(self, game, dt: float, events):
        keysdown = pygame.key.get_pressed()
        mousedown = pygame.mouse.get_pressed()

        # Look for the tilemap for collision queries
        tmap = None
        for key, entity in game.entities.items():
            if Map in entity and SpriteSheet in entity:
                tmap = entity

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

                    hoped_vel = (0, 0)
                    if keysdown[pygame.locals.K_DOWN]:
                        hoped_vel = (0, SPEED)
                        direction = 'down'
                    elif keysdown[pygame.locals.K_UP]:
                        hoped_vel = (0, -SPEED)
                        direction = 'up'
                    elif keysdown[pygame.locals.K_LEFT]:
                        hoped_vel = (-SPEED, 0)
                        direction = 'left'
                    elif keysdown[pygame.locals.K_RIGHT]:
                        hoped_vel = (SPEED, 0)
                        direction = 'right'

                    if hoped_vel != (0, 0):
                        # Step collision by one tile side at a time, by reducing the vector's magnitude to no higher than that of a tile's side
                        hoped_dist = math.ceil((math.sqrt(hoped_vel[0]**2 + hoped_vel[1]**2)) / tmap[SpriteSheet].tile_size)
                        hoped_vel = (hoped_vel[0] / hoped_dist, hoped_vel[1] / hoped_dist)

                        # Do every step we need to cover the whole movement vector
                        for i in range(hoped_dist):
                            # This is where we'd hope to be after this step
                            hoped_pos = (io.position[0] + hoped_vel[0], io.position[1] + hoped_vel[1])

                            # Do we have a tile map to check collisions against?
                            if tmap != None:
                                # TODO we check X and then Y, in that order; this is a different path to Y and then X
                                # in time, we should check that too
                                if abs(hoped_vel[0]) > 0:
                                    # Where the x extremity would be if moved
                                    intrusive_x = hoped_pos[0] + math.copysign(io.size[0] / 2, hoped_vel[0])
                                    tcollision = False

                                    # Look at all colliding tiles on the x extermity
                                    y = hoped_pos[1] - io.size[1] / 2
                                    while y < hoped_pos[1] + io.size[1] / 2:
                                        tile_x = math.floor(intrusive_x / tmap[SpriteSheet].tile_size)
                                        tile_y = math.floor(y / tmap[SpriteSheet].tile_size)
                                        
                                        if (tile_y < 0 or tile_y >= tmap[Map].height) or (tile_x < 0 or tile_x >= tmap[Map].width) or tmap[Map].grid[tile_y][tile_x] != 1:
                                            # It's off map or collidable
                                            tcollision = True
                                            break

                                        # Increment by tile size or do a special case if we're on the last tile
                                        if y != hoped_pos[1] + io.size[1] / 2 - 1 and y + tmap[SpriteSheet].tile_size >= hoped_pos[1] + io.size[1] / 2:
                                            # Last tile, check at the very bottom of the entity, so this is not missed
                                            y = hoped_pos[1] + io.size[1] / 2 - 1
                                        else:
                                            y += tmap[SpriteSheet].tile_size
                                    if tcollision:
                                        # We collided with a tile, step back a tile and position ourselves so our extremity is just touching the unreachable tile
                                        unintrusive_x = (math.floor(intrusive_x / tmap[SpriteSheet].tile_size) - math.copysign(1, hoped_vel[0])) * tmap[SpriteSheet].tile_size
                                        hoped_pos = (unintrusive_x + (tmap[SpriteSheet].tile_size / 2) - math.copysign((io.size[0] - tmap[SpriteSheet].tile_size) / 2, hoped_vel[0]), hoped_pos[1])
                                if abs(hoped_vel[1]) > 0:
                                    # Where the y extremity would be if moved
                                    intrusive_y = hoped_pos[1] + math.copysign(io.size[1] / 2, hoped_vel[1])
                                    tcollision = False

                                    # Look at all colliding tiles on the y extermity
                                    x = hoped_pos[0] - io.size[0] / 2
                                    while x < hoped_pos[0] + io.size[0] / 2:
                                        tile_y = math.floor(intrusive_y / tmap[SpriteSheet].tile_size)
                                        tile_x = math.floor(x / tmap[SpriteSheet].tile_size)

                                        if (tile_y < 0 or tile_y >= tmap[Map].height) or (tile_x < 0 or tile_x >= tmap[Map].width) or tmap[Map].grid[tile_y][tile_x] != 1:
                                            # It's off map or collidable
                                            tcollision = True
                                            break

                                        # Increment by tile size or do a special case if we're on the last tile
                                        if x != hoped_pos[0] + io.size[0] / 2 - 1 and x + tmap[SpriteSheet].tile_size >= hoped_pos[0] + io.size[0] / 2:
                                            # Last tile, check at the very bottom of the entity, so this is not missed
                                            x = hoped_pos[0] + io.size[0] / 2 - 1
                                        else:
                                            x += tmap[SpriteSheet].tile_size
                                    if tcollision:
                                        # We collided with a tile, step back a tile and position ourselves so our extremity is just touching the unreachable tile
                                        unintrusive_y = (math.floor(intrusive_y / tmap[SpriteSheet].tile_size) - math.copysign(1, hoped_vel[1])) * tmap[SpriteSheet].tile_size
                                        hoped_pos = (hoped_pos[0], unintrusive_y + (tmap[SpriteSheet].tile_size / 2) - math.copysign((io.size[1] - tmap[SpriteSheet].tile_size) / 2, hoped_vel[1]))

                            if io.position != hoped_pos:
                                io.position = hoped_pos
                                moved = True

                    # Trigger animation of this entity's sprite, if it has one
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = moved
                    if Directioned in entity:
                        entity[Directioned].direction = direction

                    # Checks if mouse is pressed
                    if mousedown:
                        mouse_x, mouse_y = pygame.mouse.get_pos()

                        # Checks if the user clicks the slots
                        if Inventory in entity:
                            inv = entity[Inventory]

                            # If mouse coordinates are within the inventory bar
                            isMouseX = mouse_x > inv.x + inv.slotOffset and mouse_x < inv.x + inv.width - inv.slotOffset
                            isMouseY = mouse_y > inv.y + inv.slotOffset and mouse_y < inv.y + inv.height - inv.slotOffset
                            if isMouseX and isMouseY:
                                pos_x = mouse_x - inv.x - inv.slotOffset

                                # If mouse clicks a slot
                                if pos_x % (inv.slotSize + inv.slotOffset) <= inv.slotSize:
                                    activeSlot = int(pos_x // (inv.slotSize + inv.slotOffset))
                                    
                                    # If the mouse is pressed, it changes the active slot
                                    if mousedown[0]:
                                        entity[Inventory].activeSlot = activeSlot

                                        # Get active item, if there is one
                                        if activeSlot * 2 < len(inv.items):
                                            activeItemKey = inv.items[activeSlot * 2]
                                            activeItemQuantity = inv.items[activeSlot * 2 + 1]

                                            entity[Inventory].activeItem = (activeItemKey, activeItemQuantity)

                                        # No hovering anymore
                                        entity[Inventory].hoverSlot = None
                                    
                                    # If the mouse only hovers, and does not click, change the hover slot
                                    else:
                                        entity[Inventory].hoverSlot = activeSlot
                                        
                            # If the mouse is out of the inventory slots, the hovered slot should no longer be highlighted
                            else:
                                entity[Inventory].hoverSlot = None
