import uuid

import random
from random import randint

import time
import random
from random import randint


from game.components import *
from game.entities import *
from game.systems.rendersystem import RenderSystem
from game.systems.userinputsystem import UserInputSystem
from game.systems.profilesystem import ProfileSystem
from game.systems.animalsystem import AnimalSystem
from game.systems.AI_system import AI_system
from game.systems.collisionsystem import CollisionSystem, CollisionCall
from game.systems.particlesystem import ParticleSystem
from game.systems.soundsystem import SoundSystem

from game.systems.plantsystem import PlantSystem

from game.systems.damagesystem import DamageSystem
from game.systems.inventorysystem import *



class GameState:
    """Our core code.
    
    Our game is made up of entities, components and systems:
    - Components are bundles of basic data that represent a certain property, e.g:
      * Drivable
      * Drawable
      * WorthMoney
    - Entities join a bunch of these to make real-world objects, e.g.:
      * Car: [Drivable(True), Drawable('./assets/car.png'), WorthMoney(500)
    - Systems update all of our entities to make things tick-over, e.g.:
      * PhysicsSystem
      * RenderSystem
      * CurrencySystem
    """

    entities = {}
    systems = []
    collisionSystem = None

    def __init__(self, framework, name, gender):
        """Creates a GameState to fit our framework, with some information about ourselves."""
        self.framework = framework
        self.screen = framework.screen
        self.net = framework.net
        self.renderSystem = RenderSystem(self.screen)
        self.collisionSystem = CollisionSystem()
        self.inventorySystem = InventorySystem()
        self.particles = ParticleSystem(self.renderSystem)

        self.plantsystem = PlantSystem()

        self.damagesystem = DamageSystem()


        # Add all systems we want to run
        self.systems.extend([
            self.plantsystem,
            ProfileSystem(name, gender),
            UserInputSystem(),

            RenderSystem(self.screen),
            SoundSystem(),

            AI_system(),
            AnimalSystem(),

            self.collisionSystem,
            self.inventorySystem,
            self.renderSystem,
            self.particles,
            SoundSystem(),
            self.damagesystem
        ])

        if self.net.is_hosting():
            # If we're hosting, we need to register that we joined our own game
            self.on_player_join(self.net.get_id())

            self.add_entity([
                BackgroundMusic (
                    path="assets/sounds/overworld.wav"
                )
            ])
    def NewPlant(self, position):
        self.add_entity([
            IngameObject(position=position,size=(64, 64)),
                
            Health(value=10), 
            Crops(name="wheat", growth_rate=3,dehydration_rate=2, max_growth_stage=4,growth_stage=0),
            SpriteSheet(path="assets/sprites/wheat.png",tile_size=16,tiles={
                'default':[0,1, 2, 3]    
            }),
            Collidable(
                call = CollisionCall(
                    start = lambda event: self.plantsystem.oncollidestart(self,event),
                    end = lambda event: self.plantsystem.oncollideend(self,event)
                )
            )
        ])

            
            # Spawn zombies
            for i in range(4):
                spawnx = random.randint(-4000, 4000)
                spawny = random.randint(-4000, 4000)
                self.add_entity(create_zombie(self, (spawnx, spawny)))

            # Spawn bounces
            for i in range(4):
                spawnx = random.randint(-4000, 4000)
                spawny = random.randint(-4000, 4000)
                self.add_entity(create_bounce((spawnx, spawny)))

            # Spawn sheep
            for i in range(30):
                spawnx = random.randint(-4000, 4000)
                spawny = random.randint(-4000, 4000)
                self.add_entity(create_sheep((spawnx, spawny)))

            # Spawn chicken
            for i in range(30):
                spawnx = random.randint(-4000, 4000)
                spawny = random.randint(-4000, 4000)
                self.add_entity(create_chicken((spawnx, spawny)))

            # We need to make all other entities at the start of the game here
            self.add_entity(create_background_music())
            self.add_entity(create_test_collision_object())


    def update(self, dt: float, events):
        """This code gets run 60fps. All of our game logic stems from updating
        our systems on our entities."""

        # Update ourselves from the network
        self.net.pull_game(self)

        # Update our systems
        for system in self.systems:
            system.update(self, dt, events)

        # Send our changes to everyone else
        self.net.push_game(self)

    def on_player_join(self, player_id):
        """This code gets run whenever a new player joins the game."""
        # Let's give them an entity that they can control

        self.add_entity([
            # They should have a position and size in game
            IngameObject(position=(0, 0), size=(64, 64)),

            # They should have a health
            Health(value=100),

            # They should be facing a certain direction
            Directioned(direction='default'),

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
                call = CollisionCall(
                    start = lambda event: print("Player Collision Start"),
                    #update = lambda event: print("Player Collision Update"),
                    end = lambda event: print("Player Collision End")
                )
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
        ])

        self.add_entity(create_player(player_id))


    def on_player_quit(self, player_id):
        """This code gets run whever a player exits the game."""
        # Remove any entities tied to them - e.g. the player they control
        tied = []
        for key, entity in list(self.entities.items()):
            if PlayerControl in entity and entity[PlayerControl].player_id == player_id:
                del self.entities[key]

    def add_entity(self, components):
        """Add an entity to the game, from a set of components. Returns a unique
        ID for the entity."""
        key = uuid.uuid4()
        self.entities[key] = {type(value): value for (value) in components}
        if IngameObject in self.entities[key]:
            self.entities[key][IngameObject].id = key
        if Collidable in self.entities[key]:
            self.registerCollisionCalls(key, self.entities[key])
        if Inventory in self.entities[key]:
            self.registerInventory(key)
        return key

    def registerCollisionCalls(self, key, entity):
        self.collisionSystem.COLLISIONCALLS[key] = entity[Collidable].call

    def registerInventory(self, key):
        self.entities[key][Collidable].call.onCollisionStart = lambda event: self.inventorySystem.itemPickedUp(self, event, key)

    def itemPickedUp(self, event):
        print(event.keys)
