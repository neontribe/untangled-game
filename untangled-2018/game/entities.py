import tmx, time
from game.components import *
from game.systems.collisionsystem import CollisionCall

def create_player(player_id, inventory_items):
    return [
        # They should have a position and size in game
        IngameObject(position=(2000, 2000), size=(64, 64)),

        # They should have a health component
        Health(value=100, maxValue=100),

        # They should have an energy component
        Energy(value=100),

        # They should have an inventory
        Inventory(inventory_items),

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
                '270':[70,71,69],
                '90':[82,83,81],
                '0':[94,95,93],
                '180':[58,59,57]
            }
        ),

        # The player who has connected con control them with the arrow keys
        PlayerControl(player_id=player_id),
        GameAction(),

        Collidable(
            call_name = "player"
        ),

        GameAction(),

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

def create_clock():
    return [
        Clock(),
        Timed()
    ]

def create_map(path):
    # Load raw tilemap from TMX
    tile_map = tmx.TileMap.load(path)

    # Convert data to dumb python types
    width = tile_map.width
    height = tile_map.height
    grid = [
        [None for x in range(tile_map.width)] for y in range(tile_map.height)
    ]

    for layer in tile_map.layers:
        if isinstance(layer,  tmx.Layer):
            for index, tile in enumerate(layer.tiles):
                x = index % width
                y = index // width
                grid[y][x] = tile.gid or 0

    # Make our component from this
    map_comp = Map(path=path, width=width, height=height, grid=grid)

    return [
        map_comp,
        SpriteSheet(
            tile_size=32,
            path="assets/tilesets/tilemap.png",
            tiles={
                'default':[0],
                '0': [0],
                '1': [1],
                '2': [2],
                '3': [3],
                '4': [4],
                '5': [5],
                '6': [6],
                '7': [7],
                '8': [8],
                '9': [9],
                '10': [10],
                '11': [11],
                '12': [12],
                '13': [13],
                '14':[14],
                '15':[15],
                '16':[16],
                '17':[17],
                '18':[18],
                '19':[19],
                '20':[20],
                '21':[21],
                '22':[22],
            },
            moving=True
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
                '270': [9, 10, 11],
                '90': [6, 7, 8],
                '0': [3, 4, 5],
                '180': [0, 1, 2]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        Health(value=80, maxValue=80),
        ChasePlayer(speed = 1),
        Collidable(
            call_name = "zombie",
            doPush = True
        ),
        Damager(
            damagemin=10, # Someone change these, they're op.
            damagemax=20,
            cooldown=1.5
        ),
        ParticleEmitter(
            particleTypes = ["circle"],
            lifespan = 120,
            colour = (0, 0, 0),
            onlyWhenMoving = True,
            velocity = (0.5,0.5),
            directionMode = 1,
            randomness = (5,5),
            size = 4,
            height = "above",
            cooldown = 1
        )
    ]
def create_skeleton(position):
    #Add monster code
    return [
        SpriteSheet(
            path='./assets/sprites/skeleton pix spritesheet.png',
            tile_size=50,
            tiles={
                'default': [0],
                '270': [7, 8, 9],
                '90': [10, 11, 12],
                '0': [4, 5, 6],
                '180': [1, 2, 3]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        Health(value=70, maxValue=70),
        ChasePlayer(speed = 1),
        Collidable(
            call_name = "zombie"
        ),
        Damager(
            damagemin=15, # Someone change these, they're op.
            damagemax=25,
            cooldown=1.5
        ),
        ParticleEmitter(
            particleTypes = ["circle"],
            lifespan = 120,
            colour = (0, 0, 0),
            onlyWhenMoving = True,
            velocity = (0.5,0.5),
            directionMode = 1,
            randomness = (5,5),
            size = 4,
            height = "above",
            cooldown = 1
        )
    ]
def create_ice_skeleton(position):
    #Add monster code
    return [
        SpriteSheet(
            path='./assets/sprites/ice skeleton pix spritesheet.png',
            tile_size=50,
            tiles={
                'default': [0],
                '270': [7, 8, 9],
                '90': [10, 11, 12],
                '0': [4, 5, 6],
                '180': [1, 2, 3]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        Health(value=100, maxValue=100),
        ChasePlayer(speed = 2),
        Collidable(
            call_name = "zombie"
        ),
        Damager(
            damagemin=15, # Someone change these, they're op.
            damagemax=25,
            cooldown=1
        ),
        ParticleEmitter(
            particleTypes = ["circle"],
            lifespan = 120,
            colour = (0, 0, 0),
            onlyWhenMoving = True,
            velocity = (0.5,0.5),
            directionMode = 1,
            randomness = (5,5),
            size = 4,
            height = "above",
            cooldown = 1
        )
    ]
def create_bounce(position):
    return [
        SpriteSheet(
            path='./assets/sprites/BOUNCE_enemy.png',
            tile_size=32,
            tiles={
                'default': [0],
                '270': [9, 10, 11],
                '90': [6, 7, 8],
                '0': [3, 4, 5],
                '180': [12, 13, 14]
            },
            moving=False
        ),
        IngameObject(position=position, size=(64, 64)),
        Directioned(direction='default'),
        ChasePlayer(speed = 2),
        Health(value=40, maxValue=40),
        Collidable(
            call_name = 'bounce',
            doPush = True
        ),
        Damager(
            damagemin=5, # Someone change these, they're op.
            damagemax=10,
            cooldown=1.5
        )
    ]


def create_sheep(position):
    return [
        SpriteSheet(
            path='./assets/sprites/sheep.png',
            tile_size=100,
            tiles={
                'default' : [0],
                '270' : [3, 4, 4],
                '90' : [0, 1, 2],
                '0' : [8, 9, 10],
                '180' : [5, 6, 7],
            },
            moving=False
        ),
        IngameObject(position=position, size=(64,64)),
        Directioned(direction='default'),
        Health(value=30, maxValue=30),
        MoveRandom()
    ]
def create_BOSS(position):
    return [
        SpriteSheet(
            path='./assets/sprites/BOSS_enemy.png',
            tile_size=32,
            tiles={
                'default' : [0],
                '270' : [0, 1, 2],
                '90' : [0, 1, 2],
                '0' : [0, 1, 2],
                '180' : [0, 1, 2],
            },
            moving=False
        ),
        IngameObject(position=position, size=(100,100)),
        Directioned(direction='default'),
        Health(value=500, maxValue=500),
        MoveRandom(),
        Collidable(
            call_name = "zombie"
        ),
        Damager(
            damagemin=25, # Someone change these, they're op.
            damagemax=75,
            cooldown=5
        )
    ]
def create_chicken(position):
    return [
        SpriteSheet(
            path='./assets/sprites/chicken.png',
            tile_size=50,
            tiles={
                'default': [0],
                '270': [1],
                '90': [0]
            },
            moving=False
        ),

        Health(value=30, maxValue=30),
        IngameObject(position=position, size=(64,64)),
        Directioned(direction='default'),
        MoveRandom(),
        IngameObject(position=position, size=(50,50)),
        Directioned(
            direction='default',
            isOnlyLR=True
        ),
        MoveRandom()

    ]

def create_plant(game, name, path, position):
    return [
        IngameObject(position=position,size=(64, 64)),
        Health(value=100, maxValue=100),
        Energy(value=0),
        WaterBar(value=3),
        Crops(name=name, growth_rate=0.05,dehydration_rate=0.05, max_growth_stage=3,growth_stage=0,plantage_time=time.time()),
        SpriteSheet(path=path,tile_size=16,tiles={
            'default': [0, 1, 2, 3]
        }),
        GameAction(),
        Collidable(
            call_name = 'plant'
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
            path='./assets/sprites/debug.png',
            tile_size=8,
            moving=False,
            tiles={
                'default':[0]
            }
        ),
        Collidable(
            call_name = 'test'
        )
    ]

def create_test_item_object(itemID, numItems, pos=(200, 300)):
    if itemID == "test-item-bounce":
        return [
            IngameObject(position=pos, size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/BOUNCE_enemy.png',
                tile_size=32,
                tiles={
                    'default': [3, 4, 5],
                },
                moving=True
            ),
            Collidable(
                call_name = 'item'
            ),
            # Every item has this component
            CanPickUp(quantity=numItems, itemID="test-item-bounce"),
            Directioned(direction='default'),
            GameAction()
        ]
    elif itemID == "water-bucket":
        return [
            IngameObject(position=pos, size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/water_bucket.png',
                tile_size=49,
                tiles={
                    'default': [0, 1, 2, 3],
                },
                moving=True
            ),
            Collidable(
                call_name = 'item'
            ),
            # Every item has this component
            CanPickUp(quantity=numItems, itemID="water-bucket"),
            Directioned(direction='default'),
            GameAction()
        ]
    elif itemID == "wheat":
        return [
            IngameObject(position=pos, size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/wheat-icon.png',
                tile_size=49,
                tiles={
                    'default': [0, 1, 2, 3],
                },
                moving=True
            ),
            Collidable(
                call_name = 'item'
            ),
            # Every item has this component
            CanPickUp(quantity=numItems, itemID="wheat"),
            Directioned(direction='default'),
            GameAction()
        ]
    else:
        return [
            IngameObject(position=pos, size=(49,49)),
            SpriteSheet(
                path='./assets/sprites/debug.png',
                tile_size=8,
                moving=False,
                tiles={
                    'default':[0]
                }
            ),
            Collidable(
                call_name = 'item'
            ),
            # Every item has this component
            CanPickUp(quantity=numItems, itemID="test-item"),
            GameAction()
        ]

def create_wand():
    return [
            IngameObject(position=(-100,100), size=(70,70)),
            SpriteSheet(
                path='./assets/sprites/wand.png',
                tile_size=8,
                moving=False,
                tiles={
                    'default':[2]
                }
            ),
            Collidable(
                call_name = 'wand'
            ),
            # Every item has this component
            CanPickUp(quantity=1,itemID="wand"),
            ParticleEmitter(
                particleTypes = ["star"],
                offset = (0,0),
                velocity = (0,-1),
                acceleration = (0,0.1),
                colour = (255, 255, 69),
                randomness = (5,0),
                lifespan = 20
            )
        ]
def create_NPC(position):
    return [
        SpriteSheet(
            path='./assets/sprites/NPC.png',
            tile_size=32,
            tiles={
                'default': [0, 1, 2],
                '270': [0, 1, 2],
                '90': [0, 1, 2],
                '0': [0, 1, 2],
                '180': [0, 1, 2]
            },
            moving=False
        ),
        Health(maxValue=200, value=200),
        IngameObject(position=position, size=(100,100)),
        Directioned(direction='default'),
        MoveRandom()
    ]
def create_house(position):
    return [
        SpriteSheet(
            path='./assets/sprites/house.png',
            tile_size=32,
            tiles={
                'default': [0]   
            },
            moving=False
        ),
        IngameObject(position=position, size=(400,400))
    ]
        
def create_item(ingameobject,spritesheet,itemID,quantity=1):
    return [
        ingameobject,
        spritesheet,
        Collidable(
            call_name = 'test'
        ),
        # Every item has this component
        CanPickUp(quantity=quantity,itemID=itemID)
    ]
