import pygame
from pygame import Rect
import math
import random
import time
from lib.system import System
from game.components import *
from game.systems.userinputsystem import get_position

class AnimalSystem(System):
    def update(self, game, dt: float, events: list):
        # Find and get the tilemap, if it exists
        tmap = None
        for key, entity in game.entities.items():
            if Map in entity and SpriteSheet in entity:
                tmap = entity
                break

        for key, entity in game.entities.items():
            if MoveRandom in entity and time.time() - entity[MoveRandom].lastmove > 0.25:
                direct = ['left', 'right', 'up', 'down']
                dire = random.choice(direct)
                velo = {
                    'left': (-10, 0),
                    'right': (10, 0),
                    'up': (0, 10),
                    'down': (0, -10)
                }[dire]


                animal_center = get_position(entity[IngameObject], velo, tmap)
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