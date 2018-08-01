from opensimplex import OpenSimplex

from tile import TileAttribute
from tile import TileType

import tmx

class Place():
    RED_SPAWN = 0
    BLUE_SPAWN = 1

class Level():
    def load_tiles(self):
        self.width = 0
        self.height = 0
        self.grid = [[]]
        self.places = {}

    def get_tile(self, x, y):
        return self.grid[y][x]

    def can_move_to(self, x, y):
        if x < 0 or x >= self.width:
            return False
        elif y < 0 or y >= self.height:
            return False
        elif self.get_tile(x, y).has_attribute(TileAttribute.COLLIDE):
            return False
        return True
    
    def is_safe(self,  x,  y):
        if self.get_tile(x,  y).has_attribute(TileAttribute.SPIKES):
            return False
        elif not self.can_move_to(x,y):
            return False
        return True
    
    def get_place(self,  place):
        return self.places[place]


class ProceduralLevel(Level):
    def __init__(self, seed, width = 50, height = 50):
        self.openSimplex = OpenSimplex(seed)
        self.load_tiles(width, height)

    def load_tiles(self, width, height):
        self.width = width
        self.height = height
        self.grid = [
            [ self.generate_grid_tile(i, j) for i in range(width) ] for j in range(height)
        ] 

    def generate_grid_tile(self, x, y):
        noise = self.openSimplex.noise2d(x / 10, y / 10)
        if (noise < 0):
            return TileType.BRICK
        else:
            return TileType.DIRT


class SaveLevel(Level):
    def __init__(self,  path):
        tile_map = tmx.TileMap.load(path)
        self.width = tile_map.width
        self.height = tile_map.height
        self.grid = [
            [None for x in range(self.width)] for y in range(self.height)
        ]
        self.places = {}
        TILES = [TileType.GRASS, TileType.STONE, TileType.CACTUS, TileType.DIRT, TileType.BIGTREE1, TileType.BIGTREE2, TileType.BIGTREE3, TileType.BIGTREE4, TileType.BUSH, TileType.TREE, TileType.SANDTREE, TileType.BLUE_BLOCK, TileType.RED_BLOCK, TileType.BLUE_SPAWN, TileType.RED_SPAWN, TileType.BRICK, TileType.BRIDGE, TileType.WATER, TileType.SHELTER, TileType.SAND, TileType.LAVA]
        for layer in tile_map.layers:
            if isinstance(layer,  tmx.Layer):
                for index, tile in enumerate(layer.tiles):
                    x = index % self.width
                    y = index // self.width
                    self.grid[y][x] = TileType.DIRT #don't default to lava, that's a stupid idea
                    for i in TILES:
                        if i.value[0][0] == tile.gid - 1:
                            self.grid[y][x] = i
            elif isinstance(layer,  tmx.ObjectGroup):
                if layer.name == 'spawns':
                    for object in layer.objects:
                        x = object.x // tile_map.tilewidth
                        y = object.y // tile_map.tileheight
                        if object.name == 'Blue':
                            type = Place.BLUE_SPAWN
                            self.places[type] = (x,  y)
                        elif object.name == 'Red':
                            type = Place.RED_SPAWN
                            self.places[type] = (x,  y)
                        
        
