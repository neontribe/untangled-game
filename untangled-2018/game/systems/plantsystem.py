from lib.system import System
from game.components import *
import pygame
import time

class PlantSystem(System):
    last_plant = 0
    colplants = []
    def enablePlant(self, key):
        self.colplants.append(key)
    def disablePlant(self, key):
        if key in self.colplants:
            self.colplants.remove(key)
    def oncollidestart(self, game, event):
        crop = None
        player = None
        for k in event.keys:
            if Crops in game.entities[k]:
                crop = game.entities[k]
                continue
            if PlayerControl in game.entities[k]:
                player = game.entities[k]
                continue
        if crop != None and player != None:
            if game.net.is_me(player[PlayerControl].player_id):
                self.enablePlant(crop[IngameObject].id)
    def oncollideend(self, game, event):
        crop = None
        player = None
        for k in event.keys:
            if Crops in game.entities[k]:
                crop = game.entities[k]
                continue
            if PlayerControl in game.entities[k]:
                player = game.entities[k]
                continue
        if crop != None and player != None:
            if game.net.is_me(player[PlayerControl].player_id):
                self.disablePlant(crop[IngameObject].id)

    def update(self, game, dt, events):
        for key,entity in game.entities.items():
            if Crops in entity:
                crops = entity[Crops]
                spritesheet = entity[SpriteSheet]
                health = entity[Health]
                plantedTime = crops.plantage_time          
                timeDifference = time.time() - plantedTime

                # Get the health value
                # Use the health value to determine when the growth stage should be changed
                if 10 < health.value < 40 :
                    crops.growth_stage = 0
                elif 40 < health.value < 60:
                    crops.growth_stage = 1
                elif 60 < health.value < 80:
                    crops.growth_stage = 2
                elif health.value > 100:
                    crops.growth_stage = 3
                if health.value > 100:
                    health.value = 101
                
                spritesheet.default_tile = crops.growth_stage
        for key,entity in dict(game.entities).items():
            if GameAction in entity and IngameObject in entity:
                if game.net.is_hosting():
                    action = entity[GameAction]
                    if action.action == 'plant' and self.last_plant + 2 < time.time():
                        io = entity[IngameObject]
                        game.NewPlant(io.position)
                        action.action = ''
                        self.last_plant = time.time()
                    if action.action == 'water':
                        for k in self.colplants:
                            health = game.entities[k][Health]
                            health.value = health.value + 3
                            action.action = ''

                        # Get the health component
                        # Add to the health.value when watered

