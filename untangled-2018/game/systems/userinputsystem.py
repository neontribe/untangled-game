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
                    if ParticleEmitter in entity:
                        if entity[ParticleEmitter].onlyWhenMoving:
                            entity[ParticleEmitter].doCreateParticles = moved

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
