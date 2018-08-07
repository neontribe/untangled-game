import pygame
from pygame import Rect
import math
import random
import time
from lib.system import System
from game.components import *

class AnimalSystem(System):
    def update(self, game, dt: float, events: list):
        for key, entity in game.entities.items():
            if MoveRandom in entity and time.time() - entity[MoveRandom].lastmove > 0.25:
                animal_center = entity[IngameObject].position
                direct = ['left', 'right', 'up', 'down']
                dire = random.choice(direct)
                if dire == 'left':
                    direction = Directioned(direction='left')
                    animal_center = (animal_center[0]-10,animal_center[1])
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'right':
                    direction = Directioned(direction='right')
                    animal_center = (animal_center[0]+10,animal_center[1])
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'up':
                    direction = Directioned(direction='up')
                    animal_center = (animal_center[0],animal_center[1]-10)
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'down':
                    direction = Directioned(direction='down')
                    animal_center = (animal_center[0],animal_center[1]+10)
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                entity[MoveRandom].lastmove = time.time()
                if Directioned in entity:
                    entity[Directioned] = direction
        

                    