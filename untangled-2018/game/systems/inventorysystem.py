from lib.system import System
from game.components import *
from game.entities import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""

    def update(self, game, dt: float, events):
        pass

    def drinkWater(self, game, entity):
        inventory = entity[Inventory]
        entity[GameAction].action = ""
        for key, data in dict(inventory.items).items():
            if inventory.items[key]["ID"] == "water-bucket" and entity[WaterBar].value != 100:
                entity[WaterBar].value = 100
                data["quantity"] -= 1
                if data["quantity"] == 0:
                    del inventory.items[key]
                return

    def mergeStacks(self, event):
        IDs = []
        entities = []
        for k in event.keys:
            entity = event.game.entities[k]
            if CanPickUp not in entity:
                return
            else:
                if entity[CanPickUp].itemID not in IDs:
                    IDs.append(entity[CanPickUp].itemID)
                entities.append(entity)
        
        if len(IDs) == 1:
            entKeep = entities[0]
            entDest = entities[1]

            if entKeep[GameAction].action == "delete" or entDest[GameAction].action == "delete":
                return

            entKeep[CanPickUp].quantity += entDest[CanPickUp].quantity

            entDest[GameAction].action = "delete"

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
        # Get the item id and quantity
        if entity[Inventory].activeItem:
            item = entity[Inventory].activeItem

            if item[0] == "sword":
                return
            
            # Sorting out the position of the new entity
            disDropping = entity[Inventory].distanceToDrop
            offsetX, offsetY = (0, 0)
            entityPos = entity[IngameObject].position

            if direction == "0" :
                offsetY = -disDropping
            elif direction in ("180", "default"):
                offsetY = disDropping
            elif direction == "270":
                offsetX = -disDropping
            elif direction == "90":
                offsetX = disDropping

            # print(entity[Inventory].mapMinY)
            # print(entity[IngameObject].position[1])

            # # If the offset is out of bounds, inverse it
            # if entityPos[1] + disDropping > entity[Inventory].mapMaxY and entityPos[1] - disDropping < entity[Inventory].mapMinY:
            #     offsetY = -offsetY
            # elif entityPos[0] + disDropping > entity[Inventory].mapMaxX and entityPos[0] - disDropping < entity[Inventory].mapMinX:
            #     offsetX = -offsetX
            
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