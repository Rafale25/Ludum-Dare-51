from heapq import heappop, heappush
from math import hypot

from src.consts import *
from src.vec import Vec2
from src import ctx

class PathFindingMap:
    def __init__(self, game):
        self.game = game

        self.dijkstra = None
        self.gradient = None

    def compute(self, positions):
        self.compute_dijsktra2(positions)
        self.computeGradient()

    def computeGradient(self):
        gradient = [0] * GRID_WIDTH * GRID_HEIGHT

        for i in range(GRID_WIDTH * GRID_HEIGHT):

            if self.dijkstra[i] < 0:
                gradient[i] = Vec2(0.0, 0.0)
                continue

            v = Vec2(0.0, 0.0)
            x, y = self.game.toXY(i)

            # size = 1
            # for gy in range(-size, size+1):
            #     for gx in range(-size, size+1):
            for gx, gy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                if x == y == 0: continue
                if not self.game.isXYInGrid(x+gx, y+gy): continue

                try:
                    index = self.game.toI(x+gx, y+gy)
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

                if not self.game.isIndexInGrid(index): continue
                if dijkstra_map[index] != -2: continue

                if self.game.grid[index] == TILE_EMPTY:
                    dijkstra_map[index] = distance

                    x, y = self.game.toXY(index)
                    for nx, ny in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        if not self.game.isXYInGrid(x+nx, y+ny): continue

                        neighbour_index = self.game.toI(x + nx, y + ny)
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
            ind = ctx.game.index_at(*enemy.pos)
            if ind is not None:
                costs[ind] += 1
        return costs

    def compute_dijsktra2(self, positions):
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

            if not self.game.isIndexInGrid(index): continue
            if dijkstra_map[index] != -2: continue

            if self.game.grid[index] == TILE_EMPTY:
                x, y = self.game.toXY(index)
                if ctx.game.enemy_manager.rage_mode:
                    pos = ctx.game.player.pos
                    dijkstra_map[index] = distance - (hypot(x-pos.x, y+pos.y)) * 0.1
                else:
                    dijkstra_map[index] = distance

                for nx, ny in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                    if not self.game.isXYInGrid(x+nx, y+ny): continue

                    neighbour_index = self.game.toI(x + nx, y + ny)     
                    new_cost = distance + 1 + costs[index]
                    heappush(indices, (new_cost, neighbour_index))

            elif self.game.grid[index] == TILE_WALL:
                dijkstra_map[index] = -1

            else:
                pass

        self.dijkstra = dijkstra_map
