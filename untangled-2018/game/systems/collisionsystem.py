from typing import Tuple
from lib.system import System
import math

class CollisionSystem(System):
    # Structure :
    # COLLISIONEVENTS.append(CollisionCall())
    # called for both entities
    COLLISIONEVENTS = []
    # key is entity key
    COLLISIONCALLS = {}

    def distanceBetween(posA: Tuple[int,int], posB: Tuple[int,int]):
        x = abs(posA[0] - posB[0])
        y = abs(posA[1] - posB[1])
        dis = math.sqrt(x**2 + y**2)
        return dis

    def checkCollisions(self, game, key, collidable, others: list):
        if others == None:
            return
        for against in others:
            if collidable == against[1]:
                continue
            else:
                rectA = collidable.toRect(game.entities[key])
                rectB = against[1].toRect(game.entities[against[0]])
                keys = [key, against[0]]
                if rectA.colliderect(rectB):
                    self.createCollision(keys)
                else:
                    self.endCollision(keys)


    def endCollision(self, keys):
        event = self.collisionExists(keys)
        if event is not None:
            event.doEnd = True


    def createCollision(self,keys: list):
        #Collide the entities
        if self.collisionExists(keys) is None:
            self.COLLISIONEVENTS.append(CollisionEvent(self, keys))

    def allExcept(self, exclude, l: list):
        ret = []
        for x in l:
            if l is not exclude:
                ret.append(l)
        return ret

    def collisionExists(self, keys: list):
        for e in self.COLLISIONEVENTS:
            c = 0
            for x in keys:
                if x in e.keys:
                    c += 1
            if c >= len(keys):
                return e
        return None

    #Must be called before render
    def update(self, game, dt, events):
        remove = []
        for c in self.COLLISIONEVENTS:
            if c.doEnd:
                c.end()
                remove.append(c)
                print("Collision Ended")
            else:
                c.update()
        for r in remove:
            self.COLLISIONEVENTS.remove(r)
            del(r)
        remove = []


class CollisionEvent:
    doEnd = False
    keys = []
    calls = []
    def __init__(self, colSystem: CollisionSystem, keys: list):
        self.keys = keys
        for k in keys:
            if colSystem.COLLISIONCALLS[k] is not None:
                self.calls.append(colSystem.COLLISIONCALLS[k])
        print("Collision Started")
        self.start()
        
    def start(self):
        for c in self.calls:
            if c.onCollisionStart != None:
                c.onCollisionStart(self)

    def update(self):
        for c in self.calls:
            if c.onCollisionUpdate != None:
                c.onCollisionUpdate(self)

    def end(self):
        for c in self.calls:
            if c.onCollisionEnd != None:
                c.onCollisionEnd(self)

class CollisionCall:
    def __init__(self, start=None, update=None, end=None):
        self.onCollisionStart = start
        self.onCollisionUpdate = update
        self.onCollisionEnd = end
    #Function with 1 parameter for CollisionEvent
    #Start of collision
    onCollisionStart = lambda: None
    #Function with 1 parameter for CollisionEvent
    #while colliding
    onCollisionUpdate = lambda: None
    #Function with 1 parameter for CollisionEvent
    #end of collision
    onCollisionEnd = lambda: None
