import pygame
from pygame import Rect

from lib.system import System
from game.components import *

import math

class MapSystem(System):
    def update(self, game, dt: float, events: list):
        pass

    def get_surrounding_blocks(grid, coords, direction):
        offs = []
        if direction == 'left':
            offs = [[-1, 0]]
        elif direction == 'right':
            offs = [[1, 0]]
        elif direction == 'up':
            offs = [[0, -1], [-1, -1]]
        elif direction == 'down':
            offs = [[-1, 1], [0, 1]]

        surrounding = []
        for off in offs:
            i = math.floor(coords[0] + off[0])
            j = math.floor(coords[1] + off[1])
            surrounding.append([i, j, grid[j][i]])
        return surrounding
