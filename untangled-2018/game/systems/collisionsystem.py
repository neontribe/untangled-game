from typing import Tuple
from components import *
from lib.system import System
import math

class CollisionSystem(System):
    def distanceBetween(posA: Tuple[int,int], posB: Tuple[int,int]):
        x = abs(posA[0] - posB[0])
        y = abs(posA[1] - posB[1])
        dis = math.sqrt(x**2 + y**2)
        return dis

    def checkCollisions(self,entity, others, ignore=[]):
        for against in others:
            if entity == against or entity in ignore or against in ignore:
                continue
            else:
                rectA = entity[Collidable].toRect()
                rectB = against[Collidable].toRect()
                if rectA.colliderect(rectB):
                    self.createCollision([entity,against])

    def createCollision(self,entities: list):
        #Collide the entities
        if not self.collisionExists(entities):
            self.COLLISIONEVENTS.append(CollisionEvent(self, entities))
        self.COLLIDING.append(entities)

    def collisionExists(self, entities: list):
        if entities in self.COLLIDING:
            return True
        for x in self.COLLIDING:
            c = 0
            for e in entities:
                if e in x:
                    c += 1
            if c >= len(entities):
                return True
        return False

    # Structure :
    # COLLISIONEVENTS[entityA] = CollisionCall()
    # called for both entities
    COLLISIONEVENTS = []
    COLLISIONCALLS = {}
    COLLIDING = []

    #Must be called before render
    def update(self, game, dt, events):
        remove = []
        for c in self.COLLISIONEVENTS:
            if c.collidingEntities in self.COLLIDING:
                c.update()
            else:
                c.end()
                remove.append(c)
        for r in remove:
            self.COLLISIONEVENTS.remove(r)
            del(r)
        remove = []
        self.COLLIDING = []


class CollisionEvent:
    collidingEntities = []
    calls = []
    def __init__(self, colSystem: CollisionSystem, entities: list):
        self.collidingEntities = entities
        for e in entities:
            if colSystem.COLLISIONCALLS[e] not None:
                self.calls.append(colSystem.COLLISIONCALLS[e])
        self.start()
        
    def start(self):
        for c in self.calls:
            c.onCollisionStart(self)

    def update(self):
        for c in self.calls:
            c.onCollisionUpdate(self)

    def end(self):
        for c in self.calls:
            c.onCollisionEnd(self)

class CollisionCall:
    def __init__(self, colSystem: CollisionSystem):
        colSystem.COLLISIONCALLS.append(self)
    #Function with 1 parameter for CollisionEvent
    #Start of collision
    onCollisionStart = lambda: pass
    #Function with 1 parameter for CollisionEvent
    #while colliding
    onCollisionUpdate = lambda: pass
    #Function with 1 parameter for CollisionEvent
    #end of collision
    onCollisionEnd = lambda: pass
