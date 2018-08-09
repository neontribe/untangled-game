from game.systems.collisionsystem import CollisionCall

class Class_Collisions:
    game = None

    def __init__(self, game):
        self.game = game

    COLLISIONS = {
        'player': CollisionCall(
            start = lambda game, event: game.inventorySystem.itemPickedUp(event)
        ),
        'zombie': CollisionCall(
            update = lambda game, event: game.damagesystem.onDamage(event)
        ),
        'test': CollisionCall(

        ),
        'bounce': CollisionCall(

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