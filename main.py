from math import dist
import random
from collections import defaultdict

import arcade

from src.consts import *
from src.player import Player
from src.enemy_mananager import EnemyManager
from src.dijsktra import PathFindingMap
from src.vec import Vec2

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Ludum Dare 51"

class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        self.pressed = defaultdict(bool)
        arcade.set_background_color(arcade.color.AMAZON)

        random.seed(69) # Haha funny

        # Get X and Y from index and width
        # y = i // GRID_WIDTH
        # x = i % GRID_WIDTH
        self.grid = [0] * GRID_WIDTH * GRID_HEIGHT

        for i in range(GRID_HEIGHT * GRID_WIDTH):
            self.grid[i] = TILE_WALL if random.random() > 0.8 else TILE_EMPTY

        self.pathFindingMap = PathFindingMap(self)

        self.player = Player(self, x=(GRID_WIDTH*GRID_SCALE)/2, y=(GRID_HEIGHT*GRID_SCALE)/2)
        self.enemy_manager = EnemyManager(self)

        self.pathFindingMap.compute(self.player.pos.x/GRID_SCALE, self.player.pos.y/GRID_SCALE)

    def tile_quantize(self, x, y):
        return Vec2(int(x / GRID_SCALE) * GRID_SCALE, int(y / GRID_SCALE) * GRID_SCALE)

    def tile_at(self, x, y):
        x /= GRID_SCALE
        y /= GRID_SCALE
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return self.grid[int(y) * GRID_WIDTH + int(x)]
        else:
            return TILE_WALL

    def isIndexInGrid(self, i):
        return 0 <= i < GRID_WIDTH * GRID_HEIGHT

    def isXYInGrid(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT

    def toI(self, x, y):
        return int(y) * GRID_WIDTH + int(x)

    def toXY(self, i):
        return (i % GRID_WIDTH, i // GRID_WIDTH)

    def on_draw(self):
        arcade.set_viewport(0, GRID_WIDTH*GRID_SCALE, 0, GRID_HEIGHT*GRID_SCALE)
        # self.pathFindingMap.compute(self.player.pos.x/GRID_SCALE, self.player.pos.y/GRID_SCALE)

        self.clear()

        for i in range(GRID_HEIGHT * GRID_WIDTH):
            y = i // GRID_WIDTH
            x = i % GRID_WIDTH

            arcade.draw_rectangle_filled(
                center_x=x*GRID_SCALE + GRID_SCALE/2,
                center_y=y*GRID_SCALE + GRID_SCALE/2,
                width=GRID_SCALE,
                height=GRID_SCALE,
                color=(0,0,0) if (self.grid[i] == 1) != self.enemy_manager.rage_mode else (150,150,150))

        self.player.draw()
        self.enemy_manager.draw()

        ## draws gradient map
        for i in range(GRID_HEIGHT * GRID_WIDTH):
            y = i // GRID_WIDTH
            x = i % GRID_WIDTH

            startx = x*GRID_SCALE + GRID_SCALE/2
            starty = y*GRID_SCALE + GRID_SCALE/2
            arcade.draw_line(
                startx,
                starty,
                startx + self.pathFindingMap.gradient[i].x,
                starty + self.pathFindingMap.gradient[i].y,
                arcade.color.RED, line_width=0.2)

        ## draws dijsktra map
        # arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
        # for i in range(GRID_HEIGHT * GRID_WIDTH):
        #     y = i // GRID_WIDTH
        #     x = i % GRID_WIDTH
        #     arcade.draw_text(str(self.pathFindingMap.dijkstra[i]),
        #         start_x=x* (SCREEN_WIDTH/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
        #         start_y=y* (SCREEN_WIDTH/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
        #         color=arcade.color.RED)

    def on_update(self, dt):
        self.player.update(dt)
        self.enemy_manager.update(dt)

    # https://api.arcade.academy/en/latest/arcade.key.html
    def on_key_press(self, key, key_modifiers):
        self.pressed[key] = True

    def on_key_release(self, key, key_modifiers):
        self.pressed[key] = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        pass

    def on_mouse_release(self, x, y, button, key_modifiers):
        pass


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()

if __name__ == "__main__":
    main()