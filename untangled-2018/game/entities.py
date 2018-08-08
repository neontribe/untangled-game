from game.components import *
from game.systems.collisionsystem import CollisionCall

def create_player(player_id):
    return [
        # They should have a position and size in game
        IngameObject(position=(0, 0), size=(64, 64)),

        # They should have a health component
        Health(value=100),

        # They should have an energy component
        Energy(value=100),

        # They should have an inventory
        Inventory([]),

        # They should be facing a certain direction
        Directioned(direction='default'),
        WaterBar(value=100),

        # They will have a name and gender
        Profile(),

        # We know what they may look like
        SpriteSheet(
            path='./assets/sprites/player.png',
            tile_size=48,
            moving=False,
            tiles={
                'default':[58],
                'left':[70,71,69],
                'right':[82,83,81],
                'up':[94,95,93],
                'down':[58,59,57]
            }
        ),

        # The player who has connected con control them with the arrow keys
        PlayerControl(player_id=player_id),
        GameAction(),

        Collidable(
            call = CollisionCall()
        ),

        ParticleEmitter(
            particleTypes = ["ring","star"],
            offset = (0,32),
            velocity = (1,1),
            directionMode = 2,
            colour = (137, 63, 69),
            onlyWhenMoving = True,
            randomness = (3,3)
        )
    ]

def create_zombie(game, position):
    #Add monster code
    return [
        SpriteSheet(
            path='./assets/sprites/ZOM_enemy.png',
            tile_size=32,
            tiles={
                'default': [0],
                'left': [9, 10, 11],
                'right': [6, 7, 8],
                'up': [3, 4, 5],
                'down': [0, 1, 2]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        ChasePlayer(speed = 1),
        Collidable(
            call = CollisionCall(
                update = lambda event: game.damagesystem.onDamage(game,event)
            )
        ),
        Damager(
            damagemin=10, # Someone change these, they're op.
            damagemax=20,
            cooldown=1.5
        )
    ]

def create_bounce(position):
    return [
        SpriteSheet(
            path='./assets/sprites/BOUNCE_enemy.png',
            tile_size=32,
            tiles={
                'default': [0],
                'left': [9, 10, 11],
                'right': [6, 7, 8],
                'up': [3, 4, 5],
                'down': [12, 13, 14]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        ChasePlayer(speed = 2)
    ]

def create_sheep(position):
    return [
        SpriteSheet(
            path='./assets/sprites/sheep.png',
            tile_size=100,
            tiles={
                'default' : [0],
                'left' : [3, 4, 4],
                'right' : [0, 1, 2],
                'up' : [8, 9, 10],
                'down' : [5, 6, 7],
            },
            moving=False
        ),
        IngameObject(position=position, size=(64,64)),
        Directioned(direction='default'),
        MoveRandom()
    ]

def create_chicken(position):
    return [
        SpriteSheet(
            path='./assets/sprites/chick5.png',
            tile_size=50,
            tiles={
                'default': [0],
                'left': [3, 3, 3],
                'right': [0, 0, 0],
                'up': [0, 0, 0],
                'down': [0, 0, 0]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64,64)),
        Directioned(direction='default'),
        MoveRandom()
    ]

def create_plant(game, name, path, position):
    return [
        IngameObject(position=position,size=(64, 64)),
        Health(value=10),
        Energy(value=0),
        WaterBar(value=50),
        Crops(name=name, growth_rate=3,dehydration_rate=2, max_growth_stage=4,growth_stage=0),
        SpriteSheet(path=path,tile_size=16,tiles={
            'default': [0, 1, 2, 3]
        }),
        Collidable(
            call = CollisionCall(
                start = lambda event: game.plantsystem.oncollidestart(game,event),
                end = lambda event: game.plantsystem.oncollideend(game,event)
            )
        )
    ]


def create_background_music():
    return [
        BackgroundMusic (
            path="assets/sounds/overworld.wav"
        )
    ]

def create_test_collision_object():
    return [
        IngameObject(position=(0,0), size=(128,128)),
        SpriteSheet(
            path='./assets/sprites/test.png',
            tile_size=8,
            moving=False,
            tiles={
                'default':[0]
            }
        ),
        Collidable(
            call = CollisionCall()
        )
    ]

def create_test_item_object(animated=False):
    if animated:
        return [
            IngameObject(position=(200,100), size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/BOUNCE_enemy.png',
                tile_size=32,
                tiles={
                    'default': [3, 4, 5],
                },
                moving=True
            ),
            Collidable(
                call = CollisionCall()
            ),
            # Every item has this component
            CanPickUp(quantity=1),
            Directioned(direction='default')
        ]
    else:
        return [
            IngameObject(position=(100,100), size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/test.png',
                tile_size=8,
                moving=False,
                tiles={
                    'default':[0]
                }
            ),
            Collidable(
                call = CollisionCall()
            ),
            # Every item has this component
            CanPickUp(quantity=2)
        ]
