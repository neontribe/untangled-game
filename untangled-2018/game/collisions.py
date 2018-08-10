from game.systems.collisionsystem import CollisionCall
from game.components import *

class Class_Collisions:
    game = None

    def __init__(self, game):
        self.game = game

    COLLISIONS = {
        'player': CollisionCall(
            start = lambda game, event: game.inventorySystem.itemPickedUp(event)
        ),
        'zombie': CollisionCall(
            update = lambda game, event: damagerUpdate(event)
        ),
        'test': CollisionCall(

        ),
        'bounce': CollisionCall(
            update = lambda game,event: damagerUpdate(event)
        ),
        'plant': CollisionCall(
            start = lambda game, event: game.plantsystem.oncollidestart(event),
            end = lambda game, event: game.plantsystem.oncollideend(event)
        )
    }

    def get_functions(self, name):
        if name in self.COLLISIONS:
            return self.COLLISIONS[name]
        else:
            print("No collision for " + name + " found")

def damagerUpdate(event):
    event.game.damagesystem.onDamage(event)
    avoidOthers(event)

def avoidOthers(event):
    entities = []
    for k in event.keys:
        entitiy = event.game.entities[k]
        if entitiy[Collidable].canCollide and entitiy[Collidable].doPush:
            entities.append(event.game.entities[k])
    if len(entities) > 1:
        posAgainst = entities[0][IngameObject].position
        posFor = entities[1][IngameObject].position
        dif = [posFor[0] - posAgainst[0], posFor[1] - posAgainst[1]]
        entities[0][IngameObject].position = (posAgainst[0] - (dif[0]/50), posAgainst[1] - (dif[1]/50))
        entities[1][IngameObject].position = (posFor[0] + (dif[0]/50), posFor[1] + (dif[1]/50))

