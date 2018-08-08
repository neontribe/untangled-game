import pygame
from pygame import Rect

from lib.system import System
from game.components import *
from game.systems.collisionsystem import *

class RenderSystem(System):
    """This system draws any entity with a SpriteSheet component."""

    def __init__(self, screen):
        self.screen = screen
        self.image_cache = {}
        self.steps = 0
        self.particles = {
            'above':[],
            'below':[]
        }
        self.particleFunc = {
            'square': lambda p, s: self.particle_square(p,s),
            'circle': lambda p, s: self.particle_circle(p,s),
            'ring': lambda p, s: self.particle_ring(p,s),
            'star': lambda p, s: self.particle_star(p,s)
        }

        font_path = 'assets/fonts/alterebro-pixel-font.ttf'
        self.font = pygame.font.Font(font_path, 45)

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

        # Draw tilemap
        for key, entity in game.entities.items():
            if Map in entity and SpriteSheet in entity:
                spritesheet = entity[SpriteSheet]
                map = entity[Map]
                for y, row in enumerate(map.grid):
                    for x, tile in enumerate(row):
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

                        self.screen.blit(image, screen_pos)

        self.draw_particles("below", our_center)

        previousCollidables = []

        # Render everything we can
        for key, entity in game.entities.items():
            #Check collisions for entity against all previously checked entities
            if IngameObject in entity and Collidable in entity:
                if entity[Collidable].canCollide:
                    game.collisionSystem.checkCollisions(game,key,entity[Collidable],previousCollidables)
                    previousCollidables.append((key,entity[Collidable]))

            if IngameObject in entity and ParticleEmitter in entity:
                new_part = entity[ParticleEmitter].getParticle(entity)
                if new_part != None:
                    game.particles.add_particle(new_part)

            # Is this an entity we should draw?
            if IngameObject in entity and SpriteSheet in entity:
                spritesheet = entity[SpriteSheet]

                # Where are they relative to us?
                pos = entity[IngameObject].position
                rel_pos = (pos[0] - our_center[0], pos[1] - our_center[1])
                screen_pos = (
                    rel_pos[0] + game.framework.dimensions[0]/2,
                    rel_pos[1] + game.framework.dimensions[1]/2
                )

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
                    img_index = img_indexes[0]
                img = self.get_image(spritesheet, img_index)
                
                #Scale the image
                if img.get_size() != entity[IngameObject].size:
                    img = pygame.transform.scale(img, entity[IngameObject].size)
                
                rect = Rect(screen_pos, entity[IngameObject].size)
                rect.center = screen_pos
                
                # Draw the image
                self.screen.blit(img, rect)

                # Center health bar and nametag
                rect.x -= 30

                # Checks if entity has a health component
                if Health in entity:
                    # Health bar wrapper
                    healthBarThickness = 2
                    pygame.draw.rect(self.screen, (255, 255, 255), (rect.x, rect.y-30, 100+healthBarThickness*2, 10), healthBarThickness)

                    # Red health bar
                    if entity[Health].value > 0:
                        currentHealthPos = (rect.x+healthBarThickness, rect.y-30+healthBarThickness, entity[Health].value, 10-healthBarThickness*2)
                        pygame.draw.rect(self.screen, (255, 0, 0), currentHealthPos)

                # Does the entity have a name we can draw
                if Profile in entity:
                    name = entity[Profile].name

                    # Draw our name with our font in white
                    rendered_text_surface = self.font.render(name, False, (0, 255, 25))


                    # Move the nametag above the player
                    rect.y -= 70

                    # Draw this rendered text we've made to the screen
                    self.screen.blit(rendered_text_surface, rect)

            self.draw_particles("above", our_center)

    def get_image(self, spritesheet, index):
        # Ideally, we cache so we only process a file once
        if spritesheet.path not in self.image_cache:
            # Load from file
            sheet_img = pygame.image.load(spritesheet.path)

            # Check the file can be divided right
            if sheet_img.get_width() % spritesheet.tile_size != 0 or sheet_img.get_height() % spritesheet.tile_size != 0:
                raise ValueError('Spritesheet width and height are not a multiple of its tile size')
            
            # Partition into sub-images
            images = []
            for y in range(0, sheet_img.get_height(), spritesheet.tile_size):
                for x in range(0, sheet_img.get_width(), spritesheet.tile_size):
                    bounds = pygame.Rect(x, y, spritesheet.tile_size, spritesheet.tile_size)
                    images.append(sheet_img.subsurface(bounds))
            self.image_cache[spritesheet.path] = images

        return self.image_cache[spritesheet.path][index]

    def draw_particles(self, height: str, our_center):
        if height in self.particles.keys():
            for p in self.particles[height]:
                self.draw_particle(p, our_center)

    def draw_particle(self, particle, our_center):
        pos = (round(particle.position[0]), round(particle.position[1]))
        rel_pos = (pos[0] - our_center[0], pos[1] - our_center[1])
        screen_pos = (rel_pos[0] + 512, rel_pos[1] + 512)
        self.particleFunc[particle.particleType](particle, screen_pos)

    def particle_square(self, p, pos):
        rect = Rect(pos[0],pos[1],8,8)
        pygame.draw.rect(self.screen,p.colour,rect)

    def particle_circle(self, p, pos):
        pygame.draw.circle(self.screen,p.colour,pos,4)
        
    def particle_ring(self, p, pos):
        pygame.draw.circle(self.screen,p.colour,pos,4,2)

    def particle_star(self, p, pos):
        hor = (
            [pos[0] - 4, pos[1]],
            [pos[0] + 4, pos[1]]
        )
        ver = (
            [pos[0], pos[1] - 4],
            [pos[0], pos[1] + 4]
        )
        pygame.draw.line(self.screen,p.colour,hor[0],hor[1],2)
        pygame.draw.line(self.screen,p.colour,ver[0],ver[1],2)
