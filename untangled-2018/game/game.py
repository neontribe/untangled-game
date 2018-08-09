import uuid
import time

from game.components import *
from game.systems.rendersystem import RenderSystem
from game.systems.userinputsystem import UserInputSystem
from game.systems.profilesystem import ProfileSystem
from game.systems.collisionsystem import CollisionSystem, CollisionCall
from game.systems.soundsystem import SoundSystem
from game.systems.inventorysystem import InventorySystem
from game.systems.actionsystem import ActionSystem

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
        self.collisionSystem = CollisionSystem()
        self.inventorySystem = InventorySystem()

        # Add all systems we want to run
        self.systems.extend([
            ProfileSystem(name, gender),
            UserInputSystem(),
            self.collisionSystem,
            self.inventorySystem,
            RenderSystem(self.screen),
            SoundSystem(),
            ActionSystem()
        ])

        # If we're hosting, we need to register that we joined our own game
        if self.net.is_hosting():
            self.on_player_join(self.net.get_id())
            self.add_entity([
                BackgroundMusic (
                    path="assets/sounds/overworld.wav"
                )
            ])
            
            # Test item
            self.add_entity([
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
                CanPickUp(itemID="test")
            ])

            # Water bucket
            self.add_entity([
                IngameObject(position=(200,100), size=(49,49)),
                SpriteSheet(
                    path='./assets/sprites/water_bucket.png',
                    tile_size=49,
                    tiles={
                        'default': [0, 1, 2, 3],
                    },
                    moving=True
                ),
                Collidable(
                    call = CollisionCall()
                ),
                # Every item has this component
                CanPickUp(itemID="water_bucket"),
                Directioned(direction='default')
            ])

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

            # They should have an inventory
            Inventory([]),

            # They should be facing a certain direction
            Directioned(direction='default'),

            # Every monster, player or NPC has this
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

            # Set action to player
            GameAction(),

            Collidable(
                call = CollisionCall(
                    #start = ,
                    #update = lambda event: print("Player Collision Update"),
                    end = lambda event: print("Item no longer exists")
                )
            )
        ])

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
        if Collidable in self.entities[key]:
            self.registerCollisionCalls(key, self.entities[key])
        if Inventory in self.entities[key]:
            self.registerInventory(key)
        return key
    
    def copy_entity(self, entity):
        """Create a new entity based on another entity's components"""
        key = uuid.uuid4()
        self.entities[key] = {type(value): value for (value) in entity.components}
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