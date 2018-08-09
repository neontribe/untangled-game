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
                    self.createCollision(game, keys)
                else:
                    self.endCollision(keys)


    def endCollision(self, keys):
        event = self.collisionExists(keys)
        if event is not None:
            event.doEnd = True


    def createCollision(self,game,keys: list):
        #Collide the entities
        if self.collisionExists(keys) is None:
            #print("Collision Created")
            self.COLLISIONEVENTS.append(CollisionEvent(game, self, keys))

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
            if c.doKill:
                remove.append(c)
                continue
            if c.doEnd:
                c.end()
                remove.append(c)
                #print("Collision Ended")
            else:
                c.update()
        for r in remove:
            self.COLLISIONEVENTS.remove(r)
            r.calls = []
            del(r)
        remove = []


class CollisionEvent:
    doEnd: bool
    keys: list
    game = None
    def __init__(self, game, colSystem: CollisionSystem, keys: list):
        self.calls = []
        self.doEnd = False
        self.doKill = False
        self.keys = keys
        self.game = game
        self.start()

    def get_entity_with_component(self, component):
        for k in self.keys:
            if component in self.game.entities[k]:
                return k, self.game.entities[k]
        return None, None
        
    def get_calls(self):
        calls = []
        for key in self.keys:
            calls.append(self.game.get_collision_functions(self.game.entities[key]))
        return calls

    def start(self):
        if not self.isValid():
            return
        for c in self.get_calls():
            if c.onCollisionStart != None:
                c.onCollisionStart(self.game, self)

    def update(self):
<<<<<<< HEAD
        for key in self.keys:
            if key not in self.game.entities:
                self.doKill = True
                return
=======
        if not self.isValid():
            return
>>>>>>> master
        for c in self.get_calls():
            if c.onCollisionUpdate != None:
                c.onCollisionUpdate(self.game, self)

    def end(self):
        if not self.isValid():
            return
        for c in self.get_calls():
            if c.onCollisionEnd != None:
                c.onCollisionEnd(self.game, self)

    def isValid(self):
        for k in self.keys:
            if k not in self.game.entities:
                self.doKill = True
                return False

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
