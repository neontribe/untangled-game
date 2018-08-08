from lib.system import System
from game.components import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""
    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, game, event, key):
        itemEntity, itemKey = self.getItemFromEvent(game, event, key)
        playerEntity = game.entities[key]
        
        if itemKey not in playerEntity[Inventory].items:
            playerEntity[Inventory].items.append(itemKey)
            playerEntity[Inventory].items.append(1)
        else:
            itemIndexInList = playerEntity[Inventory].items.index(itemKey)
            playerEntity[Inventory].items[itemIndexInList + 1] += 1

        print(playerEntity[Inventory].items)

    def getItemFromEvent(self, game, event, playerkey):
        for k in event.keys:
            if k is not playerkey:
                return (game.entities[k], k)
