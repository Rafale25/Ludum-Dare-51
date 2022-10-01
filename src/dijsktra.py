from numpy import gradient
from src.consts import *
from src.vec import Vec2

class PathFindingMap:
    def __init__(self, game):
        self.game = game

        self.dijkstra = None
        self.gradient = None

    def compute(self, x, y):
        self.computeDijsktra(x, y)
        self.computeGradient()

    def computeGradient(self):
        gradient = [0] * GRID_WIDTH * GRID_HEIGHT

        for i in range(GRID_WIDTH * GRID_HEIGHT):

            v = Vec2(0.0, 0.0)
            x, y = self.game.toXY(i)

            for gy in range(-1, 1):
                for gx in range(-1, 1):
                    if gx == 0 and gy == 0: continue

                    if self.dijkstra[self.game.toI(x+gx, y+gy)] < self.dijkstra[i]:
                        v += Vec2(gx, gy)

            try:
                v.normalize()
            except ZeroDivisionError:
                pass

            gradient[i] = v

        self.gradient = gradient



    def computeDijsktra(self, px, py):
        #TODO: add error check

        # -1 : Wall
        # -2 : not checked
        # else: distance from (x, y)

        dijkstra_map = [-2] * GRID_WIDTH * GRID_HEIGHT

        indices = []
        nextIndices = [ int(py) * GRID_WIDTH + int(px) ]

        distance = 0

        while len(nextIndices) > 0:
            indices = nextIndices
            nextIndices = []

            for index in indices:

                if not self.game.isIndexInGrid(index): continue
                if dijkstra_map[index] != -2: continue

                if self.game.grid[index] == TILE_EMPTY:
                    dijkstra_map[index] = distance

                    x, y = self.game.toXY(index)
                    for nx, ny in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        neighbour_index = self.game.toI(x + nx, y + ny)
                        nextIndices.append(neighbour_index)

                elif self.game.grid[index] == TILE_WALL:
                    dijkstra_map[index] = -1

                else:
                    pass

            distance += 1

        self.dijkstra = dijkstra_map
