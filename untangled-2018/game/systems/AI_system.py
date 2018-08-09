import pygame
from pygame import Rect
import math
from lib.system import System
from game.components import *
from game.systems.userinputsystem import get_position

class AI_system(System):
    def update(self, game, dt: float, events: list):
        ZOM_center = (0, 0)

        # Find and get the tilemap, if it exists
        tmap = None
        for key, entity in game.entities.items():
            if Map in entity and SpriteSheet in entity:
                tmap = entity
                break

        for key, entity in game.entities.items():
            #We find all AI entities
            if ChasePlayer in entity and IngameObject in entity:
                # this is a list of all player locations
                player_locations = []
                for  e_key, e_entity in game.entities.items():
                    if PlayerControl in e_entity and IngameObject in e_entity:
                        # add player location into list of locations
                        player_locations.append(e_entity[IngameObject].position)


                # for each player location find the one that is the closest
                smallest_distance = None
                e_place = None
                place = entity[IngameObject].position
                # loop over player_locations
                for loc in player_locations:
                    x_diff = place[0] - loc[0]
                    y_diff = place[1] - loc[1]
                    distance = math.sqrt(x_diff**2+y_diff**2)
                    if smallest_distance == None or distance < smallest_distance:
                        smallest_distance = distance
                        e_place = loc


                # find out the distance between the entity and the player
                # if the player location is less than the closest_location value
                # set closest_location to the player location

                if smallest_distance == None:
                    if SpriteSheet in entity:
                        entity[SpriteSheet].moving = False
                
                #Finds the difference between the player place and the monster place
                if e_place != None:
                    place = entity[IngameObject].position
                    x_diff = place[0] - e_place[0]
                    y_diff = place[1] - e_place[1]
                    #e_place is player place, place is enemy place
                    #Calculates the hypotonuese of the player and the monster to allow the monster to move diagonally
                    if abs(x_diff) > 15 or abs(y_diff) > 15:
                        distance = math.sqrt(x_diff**2+y_diff**2)
                        speed = entity[ChasePlayer].speed
                        velo = (-x_diff/distance*speed, -y_diff/distance*speed)
                        if tmap == None:
                            position = (entity[IngameObject].position[0] + velo[0], entity[IngameObject].position[1] + velo[1])
                        else:
                            position = get_position(entity[IngameObject], velo, tmap)

                        entity[IngameObject].position = position
                        if SpriteSheet in entity:
                            entity[SpriteSheet].moving = True
                        if ParticleEmitter in entity:
                            if entity[ParticleEmitter].onlyWhenMoving:
                                entity[ParticleEmitter].doCreateParticles = True

                        #Changes the direction of the monster
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
