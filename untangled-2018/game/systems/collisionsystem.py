from typing import Tuple
from components import *
import math

points = [[0,0],[1,0],[0,1],[1,1],[0.5,0.5]]

def distanceBetween(posA: Tuple[int,int], posB: Tuple[int,int]):
    x = abs(posA[0] - posB[0])
    y = abs(posA[1] - posB[1])
    dis = math.sqrt(x**2 + y**2)
    return dis

def checkCollisions(entity, others, ignore):
    for check in collidable:
        for against in collidable:
            if check == against:
                continue
            else:
                if against in ignore:
                    continue
                rectA = check[Collidable].toRect()
                rectB = against[Collidable].toRect()
                if rectA.colliderect(rectB):
                    onCollision(check,against)
        ignore.append(check)

def onCollision(entityA, entityB):
    #Collide the entities
    entityA[Collidable].onCollide(entityB)
    return True