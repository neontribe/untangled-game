from typing import Tuple
from lib.system import System
import pygame
import random

class ParticleSystem(System):
    #size is 8 x 8 ONLY
    renderSystem = None
    def __init__(self, renderSystem):
        self.image_cache = {}
        self.renderSystem = renderSystem

    def update(self, game, dt: float, events: list):
        for k, v in self.renderSystem.particles.items():
            kill = []
            for p in v:
                if p.doKill:
                    kill.append(p)
                else:
                    p.updatePos()
            for k in kill:
                v.remove(k)
                del(k)

    def add_particle(self, p):
        if p.particleType in self.renderSystem.particleFunc.keys():
            (self.renderSystem.particles["below" if p.below else "above"]).append(p)
        else:
            del(p)

    image_cache: dict = {}
    def get_image(self, path):
        # Ideally, we cache so we only process a file once
        if path not in self.image_cache:
            # Load from file
            sheet_img = pygame.image.load(spritesheet.path)
            self.image_cache[spritesheet.path] = sheet_img
        return self.image_cache[spritesheet.path]
        
        
class Particle:
    velocity: Tuple[float,float]
    acceleration: Tuple[float,float]
    position: Tuple[float,float]
    colour: Tuple[int,int,int]
    particleType: str
    lifespan: int
    doKill: bool
    below: bool
    randomness: Tuple[float,float]
    size: int

    def __init__(self, particle: str, position: Tuple[float,float], lifespan: int, velocity: Tuple[float,float] = None, colour: Tuple[int,int,int] = None, acceleration: Tuple[float,float] = None, below: bool = False, randomness: Tuple[float,float] = (1.0,1.0), size : int = 8):
        self.particleType = particle
        self.lifespan = lifespan
        self.position = position
        self.colour = colour
        self.velocity = velocity
        self.acceleration = acceleration
        self.doKill = False
        self.below = below
        self.randomness = randomness
        self.size = size

    def updatePos(self):
        if self.velocity is not None:
            if self.acceleration is not None:
                self.velocity = (self.velocity[0] + self.acceleration[0], self.velocity[1] + self.acceleration[1])
            self.position = (self.position[0] + self.velocity[0] + self.randomModi(0), self.position[1] + self.velocity[1] + self.randomModi(1))
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.kill()

    def kill(self):
        self.doKill = True

    def randomModi(self, axis):
        i = random.uniform(-10.0,10)
        return (i * self.randomness[axis])/10

    def get_random_colour():
        return random.choice([(255,0,0),(255,255,0),(0,255,0),(0,255,255),(0,0,255),(255,0,255)])
