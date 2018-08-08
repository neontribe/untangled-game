from lib.system import System
from game.components import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""
    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, game, event, key):
        itemEntity, itemKey = self.getItemFromEvent(game, event, key)

        if CanPickUp in itemEntity:
            if not itemEntity[CanPickUp].pickedUp:
                playerEntity = game.entities[key]
                
                if itemKey not in playerEntity[Inventory].items:
                    playerEntity[Inventory].items.append(itemKey)
                    playerEntity[Inventory].items.append(itemEntity[CanPickUp].quantity)
                else:
                    itemIndexInList = playerEntity[Inventory].items.index(itemKey)
                    playerEntity[Inventory].items[itemIndexInList + 1] += 1

                itemEntity[CanPickUp].pickedUp = True
                playerEntity[Inventory].activeItem = (itemKey, itemEntity[CanPickUp].quantity)

    def getItemFromEvent(self, game, event, playerkey):
        for k in event.keys:
            if k is not playerkey:
                return (game.entities[k], k)
