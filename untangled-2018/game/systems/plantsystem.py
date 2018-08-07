from lib.system import System
from game.components import *
import pygame
import time
class PlantSystem(System):
    def update(self, game, dt, events):
        for key,entity in game.entities.items():
            if Crops in entity:
                crops = entity[Crops]
                spritesheet = entity[SpriteSheet]
                plantedTime = crops.plantage_time
                timeDifference = time.time() - plantedTime
                if timeDifference > 10:
                    crops.growth_stage = 0
                elif timeDifference > 20:
                    crops.growth_stage = 1
                elif timeDifference > 30:
                    crops.growth_stage = 2
                elif timeDifference > 40:
                    crops.growth_stage = 3

                spritesheet.default_tile = crops.growth_stage
