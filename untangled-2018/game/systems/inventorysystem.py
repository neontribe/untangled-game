from lib.system import System
from game.components import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""
    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, event):
        itemKey, itemEntity = event.get_entity_with_component(CanPickUp)
        invKey, inventoryEntity = event.get_entity_with_component(Inventory)

        if itemEntity is not None:
            if not itemEntity[CanPickUp].pickedUp:
                
                if itemKey not in inventoryEntity[Inventory].items:
                    inventoryEntity[Inventory].items.append(itemKey)
                    inventoryEntity[Inventory].items.append(itemEntity[CanPickUp].quantity)
                else:
                    itemIndexInList = inventoryEntity[Inventory].items.index(itemKey)
                    inventoryEntity[Inventory].items[itemIndexInList + 1] += 1

                itemEntity[CanPickUp].pickedUp = True
                inventoryEntity[Inventory].activeItem = (itemKey, itemEntity[CanPickUp].quantity)
