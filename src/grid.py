from typing import List
from src.consts import *

class Grid:
    def __init__(self, width, height, data=None):
        self.width = width
        self.height = height
        self.grid: List[int] = data

    def __getitem__(self, index):
        return self.grid[index]

    def __setitem__(self, index, value):
        self.grid[index] = value

    def tile_quantize(self, x, y):
        return (int(x / GRID_SCALE) * GRID_SCALE, int(y / GRID_SCALE) * GRID_SCALE)

    def index_at(self, x, y):
        x /= GRID_SCALE
        y /= GRID_SCALE
        if 0 <= x < self.width and 0 <= y < self.height:
            return int(y) * self.width + int(x)
        return None

    def tile_at(self, x, y):
        x /= GRID_SCALE
        y /= GRID_SCALE
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[int(y) * self.width + int(x)]
        else:
            return TILE_WALL

    def isIndexInGrid(self, i):
        return 0 <= i < self.width * self.height

    def isXYInGrid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def toI(self, x, y):
        return int(y) * self.width + int(x)

    def toXY(self, i):
        return (i % self.width, i // self.width)
