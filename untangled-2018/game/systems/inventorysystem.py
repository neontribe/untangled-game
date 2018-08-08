from lib.system import System
from game.components import *
import pygame

class InventorySystem(System):
    """This system updates the player's inventory"""
    def update(self, game, dt: float, events):
        pass
    
    def itemPickedUp(self, game, player):
        print(game.collisionSystem.COLLISIONCALLS)