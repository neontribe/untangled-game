from lib.system import System
from game.components import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""

    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, game, event, key):
        itemEntity, itemEKey = self.getItemFromEvent(game, event, key)

        if CanPickUp in itemEntity:
            # If item can be picked up
            if not itemEntity[CanPickUp].pickedUp:
                itemID = itemEntity[CanPickUp].itemID
                playerEntity = game.entities[key]

                # Check if there are any items of that kind in the inventory already
                if itemEKey not in playerEntity[Inventory].items:
                    playerEntity[Inventory].items.append(itemEKey)
                    playerEntity[Inventory].items.append(itemID)
                    playerEntity[Inventory].items.append(itemEntity[CanPickUp].quantity)
                else:
                    itemIndexInList = playerEntity[Inventory].items.index(itemID)
                    playerEntity[Inventory].items[itemIndexInList + 1] += 1

                # Make items disappear
                itemEntity[CanPickUp].pickedUp = True
                playerEntity[Inventory].activeItem = (itemID, itemEntity[CanPickUp].quantity)

    def itemDroppedOff(self, game, entity, direction):
        itemKey = entity[Inventory].activeItem
        if itemKey:
            item = game.entities[itemKey[0]]
            itemPos = item[IngameObject].position

            disDropping = entity[Inventory].distanceToDrop

            offsetX, offsetY = (0, 0)

            if direction == "up":
                offsetY = -disDropping
            elif direction in ("down", "default"):
                offsetY = disDropping
            elif direction == "left":
                offsetX = -disDropping
            elif direction == "right":
                offsetX = disDropping
            
            if item[CanPickUp].pickedUp:
                item[IngameObject].position = (itemPos[0]+offsetX, itemPos[1]+offsetY)
                item[CanPickUp].pickedUp = False
            else:
                pass

            # Set game action to drop the uuid
            # On server side look up uuid
            # COpy components 
            # Drop on floor

    def getItemFromEvent(self, game, event, playerkey):
        for k in event.keys:
            if k is not playerkey:
                return (game.entities[k], k)
