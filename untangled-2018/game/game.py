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
from game.systems.inventorysystem import InventorySystem
from game.systems.actionsystem import ActionSystem
from game.systems.plantsystem import PlantSystem
from game.systems.damagesystem import DamageSystem
from game.systems.inventorysystem import *
from game.collisions import Class_Collisions



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

    def __init__(self, framework, name, gender, colour):
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
        self.collisions = Class_Collisions(self)


        # Add all systems we want to run
        self.systems.extend([
            self.plantsystem,
            ProfileSystem(name, gender, colour),
            UserInputSystem(),

            RenderSystem(self.screen),
            SoundSystem(),

            AI_system(),
            AnimalSystem(),

            self.collisionSystem,
            self.inventorySystem,
            ActionSystem(),
            self.renderSystem,
            self.particles,
            SoundSystem(),
            self.damagesystem
        ])

        if self.net.is_hosting():
            map_ent = self.entities[self.add_entity(create_map('assets/maps/testmap2.tmx'))]

            # If we're hosting, we need to register that we joined our own game
            self.on_player_join(self.net.get_id())

            # We need to make all other entities at the start of the game here
            self.add_entity(create_background_music())
            self.add_entity(create_test_item_object("test-item-bounce", 20))
            self.add_entity(create_test_item_object("water-bucket", 40, (400, 300)))
            self.add_entity(create_test_item_object("wheat", 40, (200, 300)))

            # TODO check we don't spawn in tiles
            # Spawn zombies
            for i in range(4):
                spawnx = random.randrange(map_ent[Map].width * map_ent[SpriteSheet].tile_size)
                spawny = random.randrange(map_ent[Map].height * map_ent[SpriteSheet].tile_size)
                self.add_entity(create_zombie(self, (spawnx, spawny)))

            # Spawn bounces
            for i in range(4):
                spawnx = random.randrange(map_ent[Map].width * map_ent[SpriteSheet].tile_size)
                spawny = random.randrange(map_ent[Map].height * map_ent[SpriteSheet].tile_size)
                self.add_entity(create_bounce((spawnx, spawny)))

            # Spawn sheep
            for i in range(30):
                spawnx = random.randrange(map_ent[Map].width * map_ent[SpriteSheet].tile_size)
                spawny = random.randrange(map_ent[Map].height * map_ent[SpriteSheet].tile_size)
                self.add_entity(create_sheep((spawnx, spawny)))

            # Spawn chicken

            for i in range(60):
                spawnx = random.randint(-2000, 2000)
                spawny = random.randint(-2000, 2000)

            for i in range(30):
                spawnx = random.randrange(map_ent[Map].width * map_ent[SpriteSheet].tile_size)
                spawny = random.randrange(map_ent[Map].height * map_ent[SpriteSheet].tile_size)

                self.add_entity(create_chicken((spawnx, spawny)))



            # We need to make all other entities at the start of the game here
            self.add_entity(create_background_music())

    def on_player_join(self, player_id):
        """This code gets run whenever a new player joins the game."""
        # Let's give them an entity that they can control
        self.add_entity(create_player(player_id))

    def on_player_quit(self, player_id):
        """This code gets run whever a player exits the game."""
        # Remove any entities tied to them - e.g. the player they control
        tied = []
        for key, entity in list(self.entities.items()):
            if PlayerControl in entity and entity[PlayerControl].player_id == player_id:
                del self.entities[key]

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
        sword_id = self.add_entity([
            SpriteSheet(
            path='./assets/sprites/Sword2.png',
            tile_size=49,
            tiles={
                'default': [0],
                'left': [1, 5, 6],
                'right': [3, 4, 7],
                'up': [0, 5, 4],
                'down': [2, 6, 7]
                },
                moving=False
            ),
            IngameObject(position=(0,0), size=(48, 48)),
            SwingSword(swing=False),
            Directioned(direction='default'),
            Damager(
                damagemin=10,
                damagemax=20,
                cooldown=1.5
            ),
            Wieldable(wielded = True)
        ])
        entity_id = self.add_entity(create_player(player_id, {0: {"ID": sword_id, "quantity": 1, "sprite": self.entities[sword_id][SpriteSheet]}}))
        self.entities[entity_id][Inventory].usedSlots[0] = True
        self.entities[sword_id][Wieldable].player_id = entity_id


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
        return key

    def itemPickedUp(self, event):
        pass

    def get_collision_functions(self, entity):
        if Collidable in entity:
            return self.collisions.get_functions(entity[Collidable].call_name)
        else:
            return None
