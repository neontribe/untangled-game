import pygame
from pygame import Rect

from lib.system import System
from game.components import *

import math

class MapSystem(System):
    def update(self, game, dt: float, events: list):
        pass

    def get_surrounding_blocks(grid, coords, dele, debug):
        surrounding = []
        for i in range(-1,3):
            for j in range(-1,3):
                x = int(math.floor(coords[0] + i))
                y = int(math.floor(coords[1] + j))
                surrounding.append([x, y, grid[y][x]])
                if dele:
                    grid[y][x] = 15
        return surrounding
