from lib.system import System
from game.components import *
from game.entities import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""

    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, event):
        itemKey, itemEntity = event.get_entity_with_component(CanPickUp)
        invKey, inventoryEntity = event.get_entity_with_component(Inventory)

        if itemEntity is not None:
            itemID = itemEntity[CanPickUp].itemID
            if not itemEntity[CanPickUp].pickedUp:
                
                if itemID not in inventoryEntity[Inventory].items:
                    inventoryEntity[Inventory].items[itemID] = (
                        itemEntity[CanPickUp].quantity,
                        itemEntity[SpriteSheet],
                        inventoryEntity[Inventory].numItems + 1
                    )
                else:
                    lItems = list(inventoryEntity[Inventory].items[itemID])
                    lItems[0] += itemEntity[CanPickUp].quantity
                    inventoryEntity[Inventory].items[itemID] = tuple(lItems)

                # Make items disappear
                itemEntity[CanPickUp].pickedUp = True
                inventoryEntity[Inventory].activeItem = (itemID, inventoryEntity[Inventory].items[itemID][0], itemEntity[SpriteSheet], inventoryEntity[Inventory].numItems + 1)
                print("Item picked up")

    def itemDroppedOff(self, game, entity, direction, typeOfDrop):
        # Get the item uuid, item id and quantity
        if entity[Inventory].activeItem:
            item = entity[Inventory].activeItem

            # Sorting out the position of the new entity
            disDropping = entity[Inventory].distanceToDrop
            offsetX, offsetY = (0, 0)
            entityPos = entity[IngameObject].position

            if direction == "up":
                offsetY = -disDropping
            elif direction in ("down", "default"):
                offsetY = disDropping
            elif direction == "left":
                offsetX = -disDropping
            elif direction == "right":
                offsetX = disDropping

            # If you drop all of the items at once
            if typeOfDrop.endswith("stack") or (typeOfDrop.endswith("one") and item[1] == 1):
                newItemEntityKey = game.add_entity(create_test_item_object(item[0], item[1]))
                newItemEntity = game.entities[newItemEntityKey]

                # Delete the items from the inventory
                entity[Inventory].items.pop(item[0], None)
            else:
                newItemEntityKey = game.add_entity(create_test_item_object(item[0], 1))

                # Decrement quantity in dict
                newActiveInInv = list(entity[Inventory].items[item[0]])
                newActiveInInv[0] -= 1
                entity[Inventory].items[item[0]] = tuple(newActiveInInv)

                # Decrement quantity in active item
                newActiveItem = list(entity[Inventory].activeItem)
                newActiveItem[1] -= 1
                entity[Inventory].activeItem = tuple(newActiveItem)

            newItemEntity = game.entities[newItemEntityKey]
            newItemEntity[IngameObject].position = (entityPos[0]+offsetX, entityPos[1]+offsetY)
            newItemEntity[CanPickUp].pickedUp = False
            
            print("I have been dropped")
            entity[GameAction].action = ""
            # Set game action to drop the uuid
            # On server side look up uuid
            # COpy components 
            # Drop on floor"""