import math
import pygame
from pygame import Rect

from lib.system import System
from game.components import *
from game.systems.collisionsystem import *

class RenderSystem(System):
    """This system draws any entity with a SpriteSheet component."""

    def __init__(self, screen, framework):
        self.lightingImg = pygame.Surface(framework.dimensions, pygame.SRCALPHA, 32).convert_alpha()
        self.lightingImg.fill((0,0,0,0))
        self.screen = screen
        self.image_cache = {}
        self.steps = 0
        self.ticks = 0
        self.particles = {
            'above':[],
            'below':[]
        }
        self.particleFunc = {
            'square': lambda p, s: self.particle_square(p,s),
            'circle': lambda p, s: self.particle_circle(p,s),
            'ring': lambda p, s: self.particle_ring(p,s),
            'star': lambda p, s: self.particle_star(p,s),
            'text': lambda p, s: self.particle_text(p,s)
        }

        font_path = 'assets/fonts/alterebro-pixel-font.ttf'
        self.font = pygame.font.Font(font_path, 45)
        self.damageFont = pygame.font.Font(font_path, 45)
        self.damageFont.set_bold(True)


    def update(self, game, dt: float, events: list):
        # Step through 15 sprite frames each second
        self.steps += dt
        frame = int(self.steps // (1.0 / 15))

        # Find our center, if we have a player to focus on
        our_center = (0, 0)
        for key, entity in game.entities.items():
            # Are they a player?
            if PlayerControl in entity and IngameObject in entity:
                # Are they us?
                if game.net.is_me(entity[PlayerControl].player_id):
                    our_center = entity[IngameObject].position
                    break
        
        invMapX = {"min": 0, "max": 0}
        invMapY = {"min": 0, "max": 0}

        # Draw tilemap
        for key, entity in game.entities.items():
            if Map in entity and SpriteSheet in entity:
                spritesheet = entity[SpriteSheet]
                map = entity[Map]
                # minimum and maximum tile indexes coordinates possible
                min_x = math.floor((our_center[0] - game.framework.dimensions[0]/2) / spritesheet.tile_size)
                min_y = math.floor((our_center[1] - game.framework.dimensions[1]/2) / spritesheet.tile_size)
                max_x = math.floor((our_center[0] + game.framework.dimensions[0]/2) / spritesheet.tile_size)
                max_y = math.floor((our_center[1] + game.framework.dimensions[1]/2) / spritesheet.tile_size)
                for y in range(min_y, max_y + 1):
                    for x in range(min_x, max_x + 1):
                        if 0 <= x < map.width and 0 <= y < map.height:
                            tile = map.grid[y][x]
                        else:
                            tile = 20
                        img_indexes = spritesheet.tiles[str(tile-1)]
                        if spritesheet.moving:
                            img_index = img_indexes[frame % len(img_indexes)]
                        else:
                            img_index = img_indexes[0]
                        image = self.get_image(spritesheet, img_index)
                        rel_pos = (
                            x * spritesheet.tile_size - our_center[0],
                            y * spritesheet.tile_size - our_center[1]
                        )

                        screen_pos = (
                            rel_pos[0] + game.framework.dimensions[0]/2,
                            rel_pos[1] + game.framework.dimensions[1]/2
                        )
                        image = image.convert()
                        alpha = math.sin(self.ticks/1000)*100
                        alpha = 100 - alpha
                        if alpha > 255:
                            alpha = 255
                        image.set_alpha(alpha)
                        self.screen.blit(image, screen_pos)

        self.draw_particles(game, "below", our_center)

        #pygame.draw.rect(self.screen,(255,0,0),Rect(0,0,self.screen.get_width(), self.screen.get_height()))

        previousCollidables = []

        # Render everything we can
        for key, entity in game.entities.items():
            r = False
            
            # Don't check for items being picked up
            if CanPickUp in entity:
                if entity[CanPickUp].pickedUp:  
                    continue
                    if Wieldable in entity:
                        wieldable = entity[Wieldable]
                        if not wieldable.wielded:
                            entity[GameAction].action = "delete"
                            continue

            #Check collisions for entity against all previously checked entities
            if IngameObject in entity and Collidable in entity:
                if entity[Collidable].canCollide:
                    game.collisionSystem.checkCollisions(game,key,entity[Collidable],previousCollidables)
                    previousCollidables.append((key,entity[Collidable]))

            if IngameObject in entity:
                # Where are they relative to us?
                pos = entity[IngameObject].position
                rel_pos = (pos[0] - our_center[0], pos[1] - our_center[1])
                screen_pos = (
                    rel_pos[0] + game.framework.dimensions[0]/2,
                    rel_pos[1] + game.framework.dimensions[1]/2
                )
                if screen_pos[0] < 0 or screen_pos[0] > self.screen.get_width() or screen_pos[1] < 0 or screen_pos[1] > self.screen.get_height():
                    continue

            if IngameObject in entity and ParticleEmitter in entity:
                if entity[ParticleEmitter].colour == (-1,-1,-1):
                    r = True
                new_particles = entity[ParticleEmitter].getParticles(entity)
                for new_part in new_particles:
                    game.particles.add_particle(new_part)

            # Is this an entity we should draw?
            if IngameObject in entity and SpriteSheet in entity:
                
                # Where are they relative to us?
                pos = entity[IngameObject].position
                rel_pos = (pos[0] - our_center[0], pos[1] - our_center[1])
                screen_pos = (
                    rel_pos[0] + game.framework.dimensions[0]/2,
                    rel_pos[1] + game.framework.dimensions[1]/2
                )

                spritesheet = entity[SpriteSheet]
                if Wieldable in entity:
                    wieldable = entity[Wieldable]
                    wielding_player = game.entities[wieldable.player_id]
                    if wieldable.wielded:
                        io = wielding_player[IngameObject]
                        entity[IngameObject].position = (io.position[0]+25,io.position[1])
                        dire = wielding_player[Directioned].direction
                        direction = Directioned(direction='default')
                        if dire ==  'left':
                            entity[IngameObject].position = (io.position[0]-25,io.position[1])
                            direction = Directioned(direction='left')
                        elif dire == 'right':
                            entity[IngameObject].position = (io.position[0]+25,io.position[1])
                            direction = Directioned(direction='right')
                        elif dire == 'up':
                            entity[IngameObject].position = (io.position[0]+25,io.position[1]-10)
                            direction = Directioned(direction='up')
                        elif dire == 'down':
                            entity[IngameObject].position = (io.position[0]-25,io.position[1]+25)
                            direction = Directioned(direction='down')
                        if Directioned in entity:
                            entity[Directioned] = direction


                img_indexes = spritesheet.tiles["default"]

                # Will they be facing a certain direction?
                if Directioned in entity:
                    alts = spritesheet.tiles[entity[Directioned].direction]
                    if alts != None:
                        img_indexes = alts
                        
                # Get the image relevent to how far through the animation we are
                if spritesheet.moving:
                    img_index = img_indexes[frame % len(img_indexes)]
                else:
                    img_index = img_indexes[spritesheet.default_tile]
                img = self.get_image(spritesheet, img_index)

                #Scale the image
                if img.get_size() != entity[IngameObject].size:
                    img = pygame.transform.scale(img, entity[IngameObject].size)
                
                rect = Rect(screen_pos, entity[IngameObject].size)
                rect.center = screen_pos
                
                # Add a rectangle behind the item because the quantity is seen outside of the item
                if CanPickUp in entity:
                    pygame.draw.circle(self.screen, (0, 255, 0), (int(rect.x + rect.width / 2), int(rect.y + rect.height / 2)), int(rect.width/2))

                # Draw the image, but only if it's on screen
                if not (rect.right < 0 or rect.left >= game.framework.dimensions[0] or rect.bottom < 0 or rect.top >= game.framework.dimensions[1]):
                    self.screen.blit(img, rect)

                # If it is an item show the amount of items there are
                if CanPickUp in entity:
                    if entity[CanPickUp].quantity > 1:
                        rendered_text_qitem = self.font.render(str(entity[CanPickUp].quantity), False, (0, 0, 0))
                        
                        self.screen.blit(rendered_text_qitem, rect)
                        
                # Center health bar and nametag
                rect.x -= 30
                # Checks if entity has an energy component
                if Energy in entity:
                    # Energy bar wrapper
                    energyBarThickness = 2
                    pygame.draw.rect(self.screen, (255, 255, 255),(rect.x, rect.y-45, 100+energyBarThickness*2, 10), energyBarThickness)
                    
                    # Yellow energy bar
                    if entity[Energy].value > 0:
                        currentEnergyPos = (rect.x+energyBarThickness, rect.y-45+energyBarThickness, entity[Energy].value, 10-energyBarThickness*2)
                        pygame.draw.rect(self.screen, (255, 255, 0), currentEnergyPos)

                # Checks if entity has a health component
                if Health in entity:
                    # Health bar wrapper
                    healthBarThickness = 2
                    pygame.draw.rect(self.screen, (255, 255, 255), (rect.x, rect.y-30, 100+healthBarThickness*2, 10), healthBarThickness)
             
                    # Red health bar
                    if entity[Health].value > 0:
                        healthValue = int(entity[Health].value / entity[Health].maxValue * 100)
                        currentHealthPos = (rect.x+healthBarThickness, rect.y-30+healthBarThickness, healthValue, 10-healthBarThickness*2)
                        pygame.draw.rect(self.screen, (255, 0, 0), currentHealthPos)

                if WaterBar in entity:
                    if not entity[WaterBar].disabled:
                        # Water bar wrapper
                        waterBarThickness = 2
                        pygame.draw.rect(self.screen, (255, 255, 255), (rect.x, rect.y-60, 100+waterBarThickness*2, 10), waterBarThickness)

                        # Blue water bar
                        if entity[Health].value > 0:
                            currentWaterPos = (rect.x+waterBarThickness, rect.y-60+waterBarThickness, entity[WaterBar].value, 10-waterBarThickness*2)
                            pygame.draw.rect(self.screen, (0, 0, 255), currentWaterPos)

                        rect.y -= 15

                # Does the entity have a name we can draw
                if Profile in entity:
                    name = entity[Profile].name

                    # Draw our name with our font in white
                    rendered_text_surface = self.font.render(name, False, entity[Profile].colour if not r else Particle.get_random_colour())

                    # Move the nametag above the player
                    rect.y -= 100

                    # Draw this rendered text we've made to the screen
                    self.screen.blit(rendered_text_surface, rect)

                # Checks if it is a player
                if PlayerControl in entity:
                    # Draw the inventory bar for us only
                    if game.net.is_me(entity[PlayerControl].player_id):
                        # Debugging if statement
                        if Inventory in entity:
                            inv = entity[Inventory]

                            # Store the map borders
                            entity[Inventory].mapMinX = invMapX["min"]
                            entity[Inventory].mapMinY = invMapY["min"]
                            entity[Inventory].mapMaxX = invMapX["max"]
                            entity[Inventory].mapMaxY = invMapY["max"]

                            # Inventory bar colours
                            inventoryBackgroundColour = (183, 92, 5)
                            slotBackgroundColour = (255, 159, 67)

                            # Draw inventory bar
                            inventoryPos = (inv.x, inv.y, inv.width, inv.height)
                            pygame.draw.rect(self.screen, inventoryBackgroundColour, inventoryPos)
                            invX = game.screen.get_width() / 2 - inv.width / 2
                            invY = game.screen.get_height() - inv.height - inv.slotOffset

                            entity[Inventory].x, entity[Inventory].y = invX, invY

                            distanceBetweenSlots = inv.slotOffset+inv.slotSize
                            # Draw slots
                            slotIndex = 0
                            for x in range(int(invX+inv.slotOffset), int(invX+inv.width), distanceBetweenSlots):
                                # The active slot has a different colour
                                if slotIndex == inv.activeSlot:
                                    colour = (241, 196, 15)
                                elif slotIndex == inv.hoverSlot:
                                    colour = (243, 156, 18)
                                else:
                                    colour = slotBackgroundColour

                                pygame.draw.rect(self.screen, colour, (x, invY+inv.slotOffset, inv.slotSize, inv.slotSize))

                                slotIndex += 1
                            
                            # Drawing items in slots
                            for slotIndex, data in entity[Inventory].items.items():
                                if data:
                                    itemImgIndexes = data['sprite'].tiles['default']
                                    itemImgIndex = itemImgIndexes[frame % len(itemImgIndexes)]

                                    # If it does, get its image
                                    itemImg = self.get_image(data['sprite'], itemImgIndex)
                                    itemW, itemH = (inv.slotSize-inv.slotOffset, inv.slotSize-inv.itemSlotOffset * 2)
                                    itemImg = pygame.transform.scale(itemImg, (itemW, itemH))

                                    # The item is placed in the slot with a 3px offset
                                    itemRect = (invX + (distanceBetweenSlots * slotIndex) + inv.itemSlotOffset, invY+inv.slotOffset + inv.itemSlotOffset, itemW, itemH)
                                    self.screen.blit(itemImg, itemRect)

                                    # Drawing text that shows how many items of this kind there are
                                    lItemRect = list(itemRect)
                                    lItemRect[1] += inv.slotOffset
                                    itemRect = tuple(lItemRect)

                                    rendered_text_qslot = self.font.render(str(data['quantity']), False, (0, 0, 128))
                                    self.screen.blit(rendered_text_qslot, itemRect)

                                slotIndex += 1
            if Clock in entity:
                time_names = ["Dusk","Dawn","Morning","Noon","Afternoon","Evening"]
                rendered_text_surface = self.font.render(time_names[entity[Clock].minute], False, (255, 255, 255))
                rect = rendered_text_surface.get_rect()
                rect.topleft= (10,5) 
                self.screen.blit(rendered_text_surface, rect)
                
                cycle= entity[Clock].cycle
                rendered_text_surface = self.font.render(str("Day"), False, (255, 255, 255))
                rect = rendered_text_surface.get_rect()
                rect.topleft= (150,5) 
                self.screen.blit(rendered_text_surface, rect)
            
                cycle= entity[Clock].cycle
                rendered_text_surface = self.font.render(str(cycle), False, (255, 255, 255))
                rect = rendered_text_surface.get_rect()
                rect.topleft= (215,5) 
                self.screen.blit(rendered_text_surface, rect)

                year= entity[Clock].year
                rendered_text_surface = self.font.render(str("Year"), False, (255, 255, 255))
                rect = rendered_text_surface.get_rect()
                rect.topleft= (270,5) 
                self.screen.blit(rendered_text_surface, rect)
            
                year= entity[Clock].year
                rendered_text_surface = self.font.render(str(year), False, (255, 255, 255))
                rect = rendered_text_surface.get_rect()
                rect.topleft= (340,5) 
                self.screen.blit(rendered_text_surface, rect)

                self.ticks = entity[Timed].time + (entity[Clock].minute * 3600) + (entity[Clock].cycle * 21600) + (entity[Clock].year * 7776000)
        self.draw_particles(game, "above", our_center)

    def get_image(self, spritesheet, index):
        # Ideally, we cache so we only process a file once
        if spritesheet.path not in self.image_cache:
            # Load from file
            sheet_img = pygame.image.load(spritesheet.path).convert_alpha()

            if isinstance(spritesheet.tile_size, tuple):
                tile_width = spritesheet.tile_size[0]
                tile_height = spritesheet.tile_size[1]
            else:
                tile_width = spritesheet.tile_size
                tile_height = spritesheet.tile_size


            # Check the file can be divided right
            if sheet_img.get_width() % tile_width != 0 or sheet_img.get_height() % tile_height != 0:
                raise ValueError('Spritesheet width and height are not a multiple of its tile size')
            
            # Partition into sub-images
            images = []
            for y in range(0, sheet_img.get_height(), tile_height):
                for x in range(0, sheet_img.get_width(), tile_width):
                    bounds = pygame.Rect(x, y, tile_width, tile_height)
                    images.append(sheet_img.subsurface(bounds))
                    
            self.image_cache[spritesheet.path] = images

        return self.image_cache[spritesheet.path][index]

    def draw_particles(self, game, height: str, our_center):
        if height in self.particles.keys():
            for p in self.particles[height]:
                self.draw_particle(game, p, our_center)

    def draw_particle(self, game, particle, our_center):
        pos = (particle.position[0], particle.position[1])
        rel_pos = (pos[0] - our_center[0], pos[1] - our_center[1])
        screen_pos = (round(rel_pos[0] + game.framework.dimensions[0] / 2), round(rel_pos[1] + game.framework.dimensions[1] / 2))
        if screen_pos[0] < 0 or screen_pos[0] > self.screen.get_width() or screen_pos[1] < 0 or screen_pos[1] > self.screen.get_height():
            particle.doKill = True
            return
        self.particleFunc[particle.particleType](particle, screen_pos)

    def particle_square(self, p, pos):
        rect = Rect(pos[0],pos[1],p.size,p.size)
        pygame.draw.rect(self.screen,p.colour,rect)

    def particle_circle(self, p, pos):
        pygame.draw.circle(self.screen,p.colour,pos,int(round(p.size/2)))
        
    def particle_ring(self, p, pos):
        pygame.draw.circle(self.screen,p.colour,pos,int(round(p.size/2)), int(math.ceil(p.size ** (1/3))))

    def particle_star(self, p, pos):
        hor = (
            [pos[0] - (p.size/2), pos[1]],
            [pos[0] + (p.size/2), pos[1]]
        )
        ver = (
            [pos[0], pos[1] - (p.size/2)],
            [pos[0], pos[1] + (p.size/2)]
        )
        pygame.draw.line(self.screen,p.colour,hor[0],hor[1],2)
        pygame.draw.line(self.screen,p.colour,ver[0],ver[1],2)

    def particle_text(self, p, pos):
        text_surface = self.damageFont.render(p.textValue,False,p.colour)
        self.screen.blit(text_surface,pos)

