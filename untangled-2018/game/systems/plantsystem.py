import math

from lib.system import System
from game.components import *
from game.entities import *
import pygame
import time
import random

class PlantSystem(System):
    last_plant = 0
    colplants = []
    def enablePlant(self, key):
        self.colplants.append(key)
    def disablePlant(self, key):
        if key in self.colplants:
            self.colplants.remove(key)
    def oncollidestart(self, event):
        cropKey, crop = event.get_entity_with_component(Crops)
        playerKey, player = event.get_entity_with_component(PlayerControl)
        if crop != None and player != None:
            if event.game.net.is_me(player[PlayerControl].player_id):
                self.enablePlant(crop[IngameObject].id)
    def oncollideend(self, event):
        cropKey, crop = event.get_entity_with_component(Crops)
        playerKey, player = event.get_entity_with_component(PlayerControl)
        if crop != None and player != None:
            if event.game.net.is_me(player[PlayerControl].player_id):
                self.disablePlant(crop[IngameObject].id)

    def update(self, game, dt, events):
        if game.net.is_hosting():
            for key,entity in game.entities.items():
                if Crops in entity:
                    crops = entity[Crops]
                    spritesheet = entity[SpriteSheet]
                    water_bar = entity[WaterBar]
                    growth_bar = entity[Energy]

                    water_bar.value = max(water_bar.value-crops.dehydration_rate, 1)

                    maxGrowth = 100

                    if water_bar.value > 1:
                        # Time to grow is inversely proportional to water bar value
                        if growth_bar.value > maxGrowth:
                            crops.growth_stage = min(crops.growth_stage+1, crops.max_growth_stage)
                            growth_bar.value = 1

                        if crops.growth_stage == crops.max_growth_stage:
                            growth_bar.value = maxGrowth
                        else:
                            growth_bar.value += crops.growth_rate

                    spritesheet.tiles['default'] = [crops.growth_stage]

            # Handle game actions
            for key,entity in dict(game.entities).items():
                if GameAction in entity and IngameObject in entity and Inventory in entity:
                    action = entity[GameAction]
                    inventory = entity[Inventory]

                    # Check if wheat is in the inventory
                    isWheatInInventory = False
                    wheatKey = 0
                    for key, data in inventory.items.items():
                        if data["ID"] == "wheat":
                            isWheatInInventory = True
                            wheatKey = key
                            break
                
                    if action.action == 'plant' and action.last_plant + 2 < time.time() and isWheatInInventory:
                        io = entity[IngameObject]
                        game.add_entity(create_plant(game, "wheat", "./assets/sprites/wheat.png", io.position))
                        action.action = ''
                        action.last_plant = time.time()

                        inventory.items[wheatKey]["quantity"] -= 1
                        if inventory.items[wheatKey]["quantity"] == 0:
                            inventory.usedSlots[wheatKey] = False
                            del inventory.items[wheatKey]
                            isWheatInInventory = False
                        else:
                            inventory.activeItem = ("wheat", inventory.items[wheatKey]["quantity"], inventory.items[wheatKey]["sprite"], wheatKey)

                    waterUsed = 0.2
                    if action.action == 'water' and entity[WaterBar].value >= waterUsed:
                        for k,e in dict(game.entities).items():
                            if Crops in e:
                                if entity[IngameObject].get_rect().colliderect(e[IngameObject].get_rect()):
                                    water_bar = e[WaterBar]
                                    water_bar.value = min(water_bar.value + waterUsed, 100)
                                    entity[WaterBar].value -= waterUsed
                                    action.action = ''
                                    if random.randint(0,2) == 0:
                                        game.particles.add_particle(
                                            Particle(
                                                colour = ((0,60,255),(65,110,255),(100,130,255))[random.randint(0,2)],
                                                particle = "square",
                                                position = [e[IngameObject].position[0] + random.randint(-30,30), e[IngameObject].position[1] + random.randint(-30,30)],
                                                velocity = (random.uniform(-1,1), random.uniform(-1,1)),
                                                lifespan = 30
                                            )
                                        )

                    if action.action == 'harvest':
                        for k,e in dict(game.entities).items():
                            if Crops in e:
                                if e[Crops].growth_stage >= e[Crops].max_growth_stage:
                                    # Are the entity and the player touching?
                                    print("I am called")
                                    if entity[IngameObject].get_rect().colliderect(e[IngameObject].get_rect()):
                                        print("Hi")
                                        if isWheatInInventory:
                                            entity[Inventory].items[wheatKey]["quantity"] += random.randint(1, 3)
                                        else:
                                            nextSlot = entity[Inventory].getFirst()
                                            if nextSlot is None:
                                                game.create_test_item_object("wheat", random.randint(1, 3), (entity[IngameObject].position))                                        
                                            else:
                                                quantity = random.randint(1, 3)
                                                entity[Inventory].items[nextSlot] = {
                                                    'ID': "wheat",
                                                    'quantity': quantity,
                                                    'sprite': SpriteSheet(
                                                                path='./assets/sprites/wheat-icon.png',
                                                                tile_size=49,
                                                                tiles={
                                                                    'default': [0, 1, 2, 3],
                                                                },
                                                                moving=True
                                                            ),
                                                }
                                                entity[Inventory].activeItem = (
                                                    entity[Inventory].items[nextSlot]['ID'],
                                                    entity[Inventory].items[nextSlot]['quantity'],
                                                    entity[Inventory].items[nextSlot]['sprite'],
                                                    nextSlot
                                                )
                                                entity[Inventory].activeSlot = nextSlot

                                        e[GameAction].action = "delete"
                                        """
                                        item_igo = IngameObject(position=entity[IngameObject].get_rect().topleft,size=(64,64))
                                        item_ss = SpriteSheet(
                                            path = 'assets/sprites/wheat.png',
                                            tile_size = 32,
                                            tiles={
                                                'default':[0]
                                            },
                                            moving=False
                                        )
                                        game.add_entity(create_item(item_igo,item_ss))
                                        action.action = ''
                                        del game.entities[k]"""
