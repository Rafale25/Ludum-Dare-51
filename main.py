from math import dist, sin, pi
import random
import time
from collections import defaultdict

import arcade

from src.consts import *
from src.player import Player
from src.enemy_manager import EnemyManager
from src.dijsktra import PathFindingMap
from src.vec import Vec2
from src import ctx

from time import perf_counter

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Ludum Dare 51"

class StartView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
        text="Press SPACE to start !!",
        bold=True,
        font_size=42,
        start_x=SCREEN_WIDTH/2,
        start_y=SCREEN_HEIGHT/2,
        anchor_x="center",
        anchor_y="center",
        rotation=sin(time.time() * 3) * 10)

    def on_update(self, dt):
        pass

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            ctx.game = GameView()
            self.window.show_view(ctx.game)

class GameOverView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)

    def on_draw(self):
        self.clear()

        arcade.draw_text(
            text="Bruh",
            bold=True,
            font_size=42,
            start_x=SCREEN_WIDTH/2,
            start_y=SCREEN_HEIGHT/2 + 50,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

        arcade.draw_text(
            text="Press Space to restart",
            bold=True,
            font_size=42,
            start_x=SCREEN_WIDTH/2,
            start_y=SCREEN_HEIGHT/2 - 50,
            anchor_x="center",
            anchor_y="center",
            rotation=sin((time.time()+4.789) * 3) * 10)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            ctx.game = GameView()
            self.window.show_view(ctx.game)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.pressed = defaultdict(bool)
        arcade.set_background_color(arcade.color.AMAZON)

        random.seed(69) # Haha funny

        # Get X and Y from index and width
        # y = i // GRID_WIDTH
        # x = i % GRID_WIDTH
        self.grid = [0] * GRID_WIDTH * GRID_HEIGHT

        for i in range(GRID_HEIGHT * GRID_WIDTH):
            self.grid[i] = TILE_WALL if random.random() > 0.8 else TILE_EMPTY

        self.shape_list_map_1 = arcade.ShapeElementList()
        self.shape_list_map_2 = arcade.ShapeElementList()
        for i in range(GRID_HEIGHT * GRID_WIDTH):
            y = i // GRID_WIDTH
            x = i % GRID_WIDTH

            shape_1 = arcade.create_rectangle_filled(
                center_x=x*GRID_SCALE + GRID_SCALE/2,
                center_y=y*GRID_SCALE + GRID_SCALE/2,
                width=GRID_SCALE,
                height=GRID_SCALE,
                color=COLOR_DARK if (self.grid[i] == TILE_WALL) else COLOR_BRIGHT)

            shape_2 = arcade.create_rectangle_filled(
                center_x=x*GRID_SCALE + GRID_SCALE/2,
                center_y=y*GRID_SCALE + GRID_SCALE/2,
                width=GRID_SCALE,
                height=GRID_SCALE,
                color=COLOR_DARK if (self.grid[i] == TILE_EMPTY) else COLOR_BRIGHT)

            self.shape_list_map_1.append(shape_1)
            self.shape_list_map_2.append(shape_2)

        self.pathFindingMap = PathFindingMap(self)

        self.player = Player(x=(GRID_WIDTH*GRID_SCALE)/2, y=(GRID_HEIGHT*GRID_SCALE)/2)
        self.enemy_manager = EnemyManager()

        self.partial_dt = 0

    def end_game(self):
        self.window.show_view(GameOverView())

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
        if self.enemy_manager.rage_mode:
            self.clear(COLOR_BRIGHT)
        else:
            self.clear(COLOR_DARK)
        # arcade.set_viewport(0, GRID_WIDTH*GRID_SCALE, 0, GRID_HEIGHT*GRID_SCALE)

        VIEWPORT_WIDTH = SCREEN_WIDTH / 20
        VIEWPORT_HEIGHT = SCREEN_HEIGHT / 20
        arcade.set_viewport(
            left=self.player.pos.x - VIEWPORT_WIDTH/2,
            right=self.player.pos.x + VIEWPORT_WIDTH/2,
            bottom=self.player.pos.y - VIEWPORT_HEIGHT/2,
            top=self.player.pos.y + VIEWPORT_HEIGHT/2
        )

        if self.enemy_manager.rage_mode:
            self.shape_list_map_2.draw()
        else:
            self.shape_list_map_1.draw()


        self.player.draw()
        self.enemy_manager.draw()



        ## draws gradient map
        if False:
            if self.pathFindingMap.gradient:
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

        time_factor = 1
        tm = (self.enemy_manager.until_rage + time_factor/2) % RAGE_DELAY
        if tm < time_factor:
            arcade.set_viewport(0, SCREEN_WIDTH, 0, SCREEN_HEIGHT)
            color = COLOR_BRIGHT if self.enemy_manager.rage_mode == (tm > time_factor/2) else COLOR_DARK
            border_width = sin((tm) / time_factor * pi) * min(SCREEN_HEIGHT, SCREEN_WIDTH)
            arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, color, border_width)

    def on_update(self, dt):
        self.partial_dt += dt
        DT = 1/60
        if self.partial_dt > 1:
            self.partial_dt = 1
        while self.partial_dt > DT:
            self.partial_dt -= DT
            self.player.update(DT)

            # t1 = perf_counter()
            self.enemy_manager.update(DT)
            # t2 = perf_counter()
            # print(f"Elapsed time: {(t2 - t1)*1000:.2f}ms {len(self.enemy_manager.enemies)}")

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
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    startView = StartView()
    window.show_view(startView)

    arcade.run()

if __name__ == "__main__":
    main()