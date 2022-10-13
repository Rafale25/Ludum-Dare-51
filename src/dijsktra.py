import time

from heapq import heappop, heappush
from math import hypot

from src.consts import *
from src.vec import Vec2
from src import ctx


MAX_TIME = 100 #milliseconds

class PathFindingMap:
    def __init__(self, game):
        self.game = game

        self.dijkstra = None
        self.gradient = None


        self.dijkstra_func_time_start = 0
        self.dijkstra_func = None

        self.gradient_func_time_start = 0
        self.gradient_func = None

    """
        Call this after compute to make it continue the computation
    """
    def update(self):
        if self.dijkstra_func:
            self.dijkstra_func_time_start = time.time()

            try:
                next(self.dijkstra_func)
            except StopIteration:
                self.dijkstra_func = None

        else:
            if self.gradient_func:
                self.gradient_func_time_start = time.time()

                try:
                    next(self.gradient_func)
                except StopIteration:
                    self.gradient_func = None

        print(self.dijkstra_func)


    def compute(self, positions):
        self.dijkstra_func = self.compute_dijsktra2(positions, MAX_TIME)
        self.gradient_func = self.computeGradient(MAX_TIME)

        # self.compute_dijsktra2(positions)
        if self.dijkstra == None:
            self.dijkstra_func_time_start = time.time()
            list(self.dijkstra_func)

        if self.gradient == None:
            self.gradient_func_time_start = time.time()
            list(self.gradient_func)

    def computeGradient(self, max_time):
        gradient = [0] * GRID_WIDTH * GRID_HEIGHT

        for i in range(GRID_WIDTH * GRID_HEIGHT):

            t = time.time()
            if (t - self.gradient_func_time_start) * 1000 > max_time:
                yield

            if self.dijkstra[i] < 0:
                gradient[i] = Vec2(0.0, 0.0)
                continue

            v = Vec2(0.0, 0.0)
            x, y = self.game.grid.toXY(i)

            # size = 1
            # for gy in range(-size, size+1):
            #     for gx in range(-size, size+1):
            for gx, gy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                if x == y == 0: continue
                if not self.game.grid.isXYInGrid(x+gx, y+gy): continue

                try:
                    index = self.game.grid.toI(x+gx, y+gy)
                    if ctx.game.enemy_manager.rage_mode:
                        if self.dijkstra[index] >= 0 and self.dijkstra[index] > self.dijkstra[i]:
                            v.x -= gx
                            v.y -= gy
                    else:
                        if self.dijkstra[index] >= 0 and self.dijkstra[index] < self.dijkstra[i]:
                            v.x += gx
                            v.y += gy
                except IndexError:
                    pass

            v.normalize()

            gradient[i] = v

        self.gradient = gradient

    def computeDijsktra(self, px, py):
        #TODO: add error check

        # -1 : Wall
        # -2 : not checked
        # else: distance from (x, y)

        dijkstra_map = [-2] * GRID_WIDTH * GRID_HEIGHT

        indices = []
        nextIndices = [ (int(py) * GRID_WIDTH + int(px)) ]

        distance = 0

        while len(nextIndices) > 0:
            indices = nextIndices
            nextIndices = []

            for index in indices:

                if not self.game.grid.isIndexInGrid(index): continue
                if dijkstra_map[index] != -2: continue

                if self.game.grid[index] == TILE_EMPTY:
                    dijkstra_map[index] = distance

                    x, y = self.game.grid.toXY(index)
                    for nx, ny in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        if not self.game.grid.isXYInGrid(x+nx, y+ny): continue

                        neighbour_index = self.game.grid.toI(x + nx, y + ny)
                        nextIndices.append(neighbour_index)

                elif self.game.grid[index] == TILE_WALL:
                    dijkstra_map[index] = -1

                else:
                    pass

            distance += 1

        self.dijkstra = dijkstra_map

    def calc_costs(self):
        costs = [0] * GRID_WIDTH * GRID_HEIGHT
        for enemy in ctx.game.enemy_manager.enemies:
            ind = ctx.game.grid.index_at(*enemy.pos)
            if ind is not None:
                costs[ind] += 1
        return costs

    def compute_dijsktra2(self, positions, max_time):
        #TODO: add error check

        # -1 : Wall
        # -2 : not checked
        # else: distance from (x, y)

        dijkstra_map = [-2] * GRID_WIDTH * GRID_HEIGHT
        costs = self.calc_costs()
        indices = [(0, (int(py) * GRID_WIDTH + int(px))) for (px, py) in positions]

        distance = 0

        while len(indices) > 0:
            distance, index = heappop(indices)

            t = time.time()
            if (t - self.dijkstra_func_time_start) * 1000 > max_time:
                yield

            if not self.game.grid.isIndexInGrid(index): continue
            if dijkstra_map[index] != -2: continue

            if self.game.grid[index] == TILE_EMPTY:
                x, y = self.game.grid.toXY(index)
                dijkstra_map[index] = distance

                for nx, ny in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    if not self.game.grid.isXYInGrid(x+nx, y+ny): continue

                    neighbour_index = self.game.grid.toI(x + nx, y + ny)
                    new_cost = distance + 1 + costs[index]
                    heappush(indices, (new_cost, neighbour_index))

            elif self.game.grid[index] == TILE_WALL:
                dijkstra_map[index] = -1

            else:
                pass

        self.dijkstra = dijkstra_map
