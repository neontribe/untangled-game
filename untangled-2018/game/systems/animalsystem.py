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
                    animal_center = (animal_center[0]-10,animal_center[1])
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'right':
                    animal_center = (animal_center[0]+10,animal_center[1])
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'up':
                    animal_center = (animal_center[0],animal_center[1]-10)
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                elif dire == 'down':
                    animal_center = (animal_center[0],animal_center[1]+10)
                    entity[IngameObject].position = animal_center
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = True
                entity[MoveRandom].lastmove = time.time()
                if Directioned in entity:
                    if not entity[Directioned].isOnlyLR:
                        entity[Directioned].direction = dire
                    else:
                        if dire != 'up' and dire != 'down':
                            entity[Directioned].direction = dire
        

                    