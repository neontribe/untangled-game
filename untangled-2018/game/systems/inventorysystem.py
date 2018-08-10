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
            # Get item ID
            itemID = itemEntity[CanPickUp].itemID

            # Check if it was picked up
            if not itemEntity[CanPickUp].pickedUp:

                # Get all existing IDs in the inventory
                existingIDS = inventoryEntity[Inventory].getIDs()
                nextActive = None

                # If there is no ID, create a new slot, with the next available slot
                if itemID not in existingIDS:
                    nextSlot = inventoryEntity[Inventory].getFirst()
                    # Add the item in the free slot
                    if nextSlot is not None:
                        inventoryEntity[Inventory].items[nextSlot] = {
                            'ID': itemID,
                            'quantity': itemEntity[CanPickUp].quantity,
                            'sprite': itemEntity[SpriteSheet]
                        }
                        nextActive = (
                            inventoryEntity[Inventory].items[nextSlot]['ID'],
                            inventoryEntity[Inventory].items[nextSlot]['quantity'],
                            inventoryEntity[Inventory].items[nextSlot]['sprite'],
                            nextSlot
                        )
                else:
                    
                    # Look for the slot with the ID
                    nextSlot = 0
                    for i, k in inventoryEntity[Inventory].items.items():
                        if k['ID'] == itemID:
                            nextSlot = i

                    # Add the quantity
                    inventoryEntity[Inventory].items[nextSlot]['quantity'] += itemEntity[CanPickUp].quantity
                    nextActive = (
                        inventoryEntity[Inventory].items[nextSlot]['ID'],
                        inventoryEntity[Inventory].items[nextSlot]['quantity'],
                        inventoryEntity[Inventory].items[nextSlot]['sprite'],
                        nextSlot
                    )

                # Make items disappear
                itemEntity[CanPickUp].pickedUp = True
                inventoryEntity[Inventory].activeItem = nextActive
                inventoryEntity[Inventory].activeSlot = nextSlot
                inventoryEntity[Inventory].usedSlots[nextSlot] = True

    def itemDroppedOff(self, game, entity, direction, typeOfDrop):
        # Get the item uuid, item id and quantity
        if entity[Inventory].activeItem:
            item = entity[Inventory].activeItem
            print(item)

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

            # If you drop all of the items at once]
            if typeOfDrop.endswith("stack") or (typeOfDrop.endswith("one") and item[1] == 1):
                newItemEntityKey = game.add_entity(create_test_item_object(item[0], item[1]))
                
                # Delete the items from the inventory
                entity[Inventory].items.pop(item[3], None)

                # IF YOU WANT DUPLICATE ITEMS, COMMENT THIS LINE
                entity[Inventory].activeItem = ()

                entity[Inventory].usedSlots[item[3]] = False
            else:
                newItemEntityKey = game.add_entity(create_test_item_object(item[0], 1))

                # Decrement quantity in activeItem
                entity[Inventory].items[item[3]]['quantity'] -= 1

                # Decrement quantity in active item
                newActiveItem = list(entity[Inventory].activeItem)
                newActiveItem[1] -= 1
                entity[Inventory].activeItem = tuple(newActiveItem)

            newItemEntity = game.entities[newItemEntityKey]
            newItemEntity[IngameObject].position = (entityPos[0]+offsetX, entityPos[1]+offsetY)
            newItemEntity[CanPickUp].pickedUp = False
            
            entity[GameAction].action = ""