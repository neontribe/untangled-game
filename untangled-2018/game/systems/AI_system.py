import pygame
from pygame import Rect
import math
from lib.system import System
from game.components import *
class AI_system(System):
    def update(self, game, dt: float, events: list):
        ZOM_center = (0, 0)
        for key, entity in game.entities.items():
            
            if ChasePlayer in entity and IngameObject in entity:
                e_place = None
                for  e_key, e_entity in game.entities.items():
                    if PlayerControl in e_entity and IngameObject in e_entity:
                        e_place = e_entity[IngameObject].position
                        break
                if e_place != None:
                    place = entity[IngameObject].position
                    x_diff = place[0] - e_place[0]
                    y_diff = place[1] - e_place[1]
                    #e_place is player place, place is enemy place
                    if abs(x_diff) > 15 or abs(y_diff) > 15:
                        distance = math.sqrt(x_diff**2+y_diff**2)
                        speed = entity[ChasePlayer].speed
                        place = (place[0]-x_diff/distance*speed,place[1]-y_diff/distance*speed)
                        entity[IngameObject].position = place
                        if SpriteSheet in entity:
                            entity[SpriteSheet].moving = True


                        if abs(x_diff) > abs(y_diff):
                            if e_place[0] >= place[0]:
                                direction = Directioned(direction='right')
                            else:
                                direction = Directioned(direction='left')
                        else:
                            if e_place[1] >= place[1]:
                                direction = Directioned(direction='down')
                            else:
                                direction = Directioned(direction='up')
                        if Directioned in entity:
                            entity[Directioned] = direction
                    else:
                        if SpriteSheet in entity:
                            entity[SpriteSheet].moving = False
                    
