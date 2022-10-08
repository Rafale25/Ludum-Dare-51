from math import sin, pi
import random
import time
from collections import defaultdict
from typing import List

import opensimplex
import arcade

from src.consts import *
from src.player import Player
from src.enemy_manager import EnemyManager
from src.dijsktra import PathFindingMap
from src.vec import Vec2
from src import ctx
from src.maze import Maze
from src.glow import Glow
from src.grid import Grid

from pathlib import Path

# from time import perf_counter

SCREEN_TITLE = "Run Hunt Repeat"
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

RATIO = SCREEN_WIDTH / SCREEN_HEIGHT
VIEWPORT_SCALE = 1
VIEWPORT_WIDTH = 32 * RATIO * VIEWPORT_SCALE
VIEWPORT_HEIGHT = 32 * VIEWPORT_SCALE

class MenuView(arcade.View):
    def __init__(self, parent_view):
        super().__init__()
        self.parent_view = parent_view

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):
        pass

    def on_draw(self):
        self.clear()

        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_update(self, dt):
        pass

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.ESCAPE:
            self.window.show_view(self.parent_view)

        if key == arcade.key.F11:
            self.window.set_fullscreen(
                True - self.window.fullscreen
            )

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.setup()

class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        self.time_start = time.time()
        self.program = self.window.ctx.program(
            vertex_shader=Path('assets/shaders/background.vs').read_text(),
            fragment_shader=Path('assets/shaders/background_blue.fs').read_text()
        )

        self.setup()

    def setup(self):
        self.screen_quad = arcade.gl.geometry.quad_2d_fs()
        self.program['resolution'] = self.window.size

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        self.program['time'] = time.time() - self.time_start
        self.screen_quad.render(program=self.program)

        arcade.set_viewport(0, self.window.width, 0, self.window.height)

        arcade.draw_text(
            text="Press SPACE to start !!",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
            start_x=self.window.width/2,
            start_y=self.window.height/2,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

    def on_update(self, dt):
        pass

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            ctx.game = GameView()
            self.window.show_view(ctx.game)

        if key == arcade.key.F11:
            self.window.set_fullscreen(
                True - self.window.fullscreen
            )

        if key == arcade.key.ESCAPE:
            self.window.show_view( MenuView(self) )

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.setup()

class GameOverView(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.score = score

        self.time_start = time.time()
        self.program = self.window.ctx.program(
            vertex_shader=Path('assets/shaders/background.vs').read_text(),
            fragment_shader=Path('assets/shaders/background_red.fs').read_text()
        )

        self.setup()

    def setup(self):
        self.screen_quad = arcade.gl.geometry.quad_2d_fs()
        self.program['resolution'] = self.window.size

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        self.program['time'] = time.time() - self.time_start
        self.screen_quad.render(program=self.program)

        arcade.set_viewport(0, self.window.width, 0, self.window.height)

        arcade.draw_text(
            text=f"Your score is {int(self.score)}",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
            start_x=self.window.width/2,
            start_y=self.window.height/2 + 75,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

        arcade.draw_text(
            text="Press Space to restart",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
            start_x=self.window.width/2,
            start_y=self.window.height/2 - 75,
            anchor_x="center",
            anchor_y="center",
            rotation=sin((time.time()+4.789) * 3) * 10)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            ctx.game = GameView()
            self.window.show_view(ctx.game)

        if key == arcade.key.F11:
            self.window.set_fullscreen(
                True - self.window.fullscreen
            )

        # if key == arcade.key.ESCAPE:
        #     self.window.show_view( MenuView(self) )

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.glow = Glow(self.window.ctx)

        self.pressed = defaultdict(bool)
        arcade.set_background_color(arcade.color.AMAZON)

        self.camera_center = Vec2(0, 0)

        self.grid = Grid(
            width=GRID_WIDTH,
            height=GRID_HEIGHT,
            data=Maze.generate(GRID_WIDTH//2 + 1, GRID_HEIGHT//2 + 1).to_grid()
        )

        ## remove walls inside radius at center
        CENTER_HOLE_RADIUS = 1
        for y in range(-CENTER_HOLE_RADIUS, CENTER_HOLE_RADIUS+1):
            for x in range(-CENTER_HOLE_RADIUS, CENTER_HOLE_RADIUS+1):
                i = self.grid.toI(GRID_WIDTH//2 + x, GRID_HEIGHT//2 + y)
                self.grid[i] = TILE_EMPTY

        ## remove walls at and random and with simplex noise
        t = int(time.time())
        opensimplex.seed(t)
        random.seed(t)
        for i in range(GRID_HEIGHT * GRID_WIDTH):
            y = i // GRID_WIDTH
            x = i % GRID_WIDTH

            # remove wall at random
            if random.random() > 0.9:
                self.grid[i] = TILE_EMPTY

            # remove wall based on simple noise
            if opensimplex.noise2(x*0.4, y*0.4) > 0.2:
                self.grid[i] = TILE_EMPTY

        ## walls and floor
        self.shape_list_map_1_wall = arcade.ShapeElementList()
        self.shape_list_map_1_empty = arcade.ShapeElementList()
        self.shape_list_map_2_wall = arcade.ShapeElementList()
        self.shape_list_map_2_empty = arcade.ShapeElementList()
        for i in range(GRID_HEIGHT * GRID_WIDTH):
            y = i // GRID_WIDTH
            x = i % GRID_WIDTH

            if self.grid[i] == TILE_WALL:
                shape_1 = arcade.create_rectangle_filled(
                    center_x=x*GRID_SCALE + GRID_SCALE/2,
                    center_y=y*GRID_SCALE + GRID_SCALE/2,
                    width=GRID_SCALE,
                    height=GRID_SCALE,
                    color=COLOR_DARK)

                shape_2 = arcade.create_rectangle_filled(
                    center_x=x*GRID_SCALE + GRID_SCALE/2,
                    center_y=y*GRID_SCALE + GRID_SCALE/2,
                    width=GRID_SCALE,
                    height=GRID_SCALE,
                    color=COLOR_BRIGHT_2)

                self.shape_list_map_1_wall.append(shape_1)
                self.shape_list_map_2_wall.append(shape_2)

            if self.grid[i] == TILE_EMPTY:
                shape_1 = arcade.create_rectangle_filled(
                    center_x=x*GRID_SCALE + GRID_SCALE/2,
                    center_y=y*GRID_SCALE + GRID_SCALE/2,
                    width=GRID_SCALE,
                    height=GRID_SCALE,
                    color=COLOR_BRIGHT_2)

                shape_2 = arcade.create_rectangle_filled(
                    center_x=x*GRID_SCALE + GRID_SCALE/2,
                    center_y=y*GRID_SCALE + GRID_SCALE/2,
                    width=GRID_SCALE,
                    height=GRID_SCALE,
                    color=COLOR_DARK)

                self.shape_list_map_1_empty.append(shape_1)
                self.shape_list_map_2_empty.append(shape_2)

        self.pathFindingMap = PathFindingMap(self)

        self.player = Player(x=(GRID_WIDTH*GRID_SCALE)/2, y=(GRID_HEIGHT*GRID_SCALE)/2)
        self.enemy_manager = EnemyManager()

        ## blood
        self.blood_splashes: List[Vec2] = []
        self.sprite_list_blood = arcade.SpriteList()
        arcade.Sprite("assets/blood.png", scale=0.002) # preload this sprite

        self.partial_dt = 0
        self.score = 0
        self.sound_limit = 0

    def end_game(self):
        arcade.play_sound(SOUND_GAME_OVER, volume=VOLUME)
        self.window.show_view( GameOverView(self.score) )

    def on_draw(self):
        glow_enabled = self.enemy_manager.rage_mode

        if glow_enabled:
            self.glow.use()

        bg_color = COLOR_BRIGHT if self.enemy_manager.rage_mode else COLOR_DARK

        if glow_enabled:
            self.glow.fb.clear(bg_color)

        if self.enemy_manager.rage_mode:
            self.clear(COLOR_BRIGHT)
        else:
            self.clear(bg_color)


        # arcade.set_viewport(0, GRID_WIDTH*GRID_SCALE, 0, GRID_HEIGHT*GRID_SCALE)
        ratio = self.window.aspect_ratio
        arcade.set_viewport(
            left=self.camera_center.x - VIEWPORT_WIDTH/2,
            right=self.camera_center.x + VIEWPORT_WIDTH/2,
            bottom=self.camera_center.y - VIEWPORT_WIDTH/ratio/2,
            top=self.camera_center.y + VIEWPORT_WIDTH/ratio/2
        )


        if self.enemy_manager.rage_mode:
            self.shape_list_map_2_empty.draw()
        else:
            self.shape_list_map_1_empty.draw()

        self.sprite_list_blood.draw()

        if self.enemy_manager.rage_mode:
            self.shape_list_map_2_wall.draw()
        else:
            self.shape_list_map_1_wall.draw()

        self.player.draw()
        self.enemy_manager.draw()

        # t1 = perf_counter()
        # t2 = perf_counter()
        # print(f"Elapsed time: {(t2 - t1)*1000:.2f}ms {len(self.enemy_manager.enemies)}")

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

        arcade.set_viewport(0, self.window.width, 0, self.window.height)

        ## draws dijsktra map
        if False:
            for i in range(GRID_HEIGHT * GRID_WIDTH - 100):
                y = i // GRID_WIDTH
                x = i % GRID_WIDTH
                arcade.draw_text(str(self.pathFindingMap.dijkstra[i]),
                    start_x=x * (self.window.width/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
                    start_y=y * (self.window.width/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
                    color=arcade.color.RED)

        time_factor = 1
        tm = (self.enemy_manager.until_rage + time_factor/2) % RAGE_DELAY

        if tm < time_factor:
            bright = COLOR_BRIGHT if glow_enabled else COLOR_BRIGHT_2
            color = bright if self.enemy_manager.rage_mode == (tm > time_factor/2) else COLOR_DARK
            border_width = sin((tm) / time_factor * pi) * min(self.window.height, self.window.width)
            arcade.draw_rectangle_outline(self.window.width / 2, self.window.height / 2, self.window.width, self.window.height, color, border_width)

        if glow_enabled:
            self.glow.render(self.window.ctx.screen)

        arcade.draw_text(f"Score: {int(self.score)}", self.window.width/2, self.window.height-20, color=arcade.color.SAE, anchor_x='center', anchor_y='center', font_name=FONT, font_size=16)

    def alloc_sound(self):
        if self.sound_limit > 1:
            self.sound_limit -= 1
            return True
        return False

    def on_update(self, dt):
        self.score += SCORE_PER_SECOND * dt
        self.partial_dt += dt
        if self.sound_limit < 8:
            self.sound_limit += 8 * dt
        DT = 1/60
        if self.partial_dt > 1:
            self.partial_dt = 1
        while self.partial_dt > DT:
            self.partial_dt -= DT
            self.player.update(DT)

            self.enemy_manager.update(DT)

            for x, y in self.blood_splashes:
                blood_sprite = arcade.Sprite("assets/blood.png", scale=0.002, center_x=x, center_y=y, angle=random.randrange(0, 360))
                self.sprite_list_blood.append(blood_sprite)
            self.blood_splashes = []

            self.camera_center = self.camera_center + (self.player.pos - self.camera_center) * 0.3

    def on_key_press(self, key, key_modifiers):
        self.pressed[key] = True

        if key == arcade.key.F11:
            self.window.set_fullscreen(
                True - self.window.fullscreen
            )

        # if key == arcade.key.ESCAPE:
        #     self.window.show_view( MenuView(self) )

    def on_key_release(self, key, key_modifiers):
        self.pressed[key] = False

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.glow.gen_fbs((width, height))


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True)
    window.set_minimum_size(720, 480)
    window.set_vsync(True)
    window.set_mouse_visible(False)

    arcade.load_font("assets/BebasNeue-Regular.ttf")
    arcade.play_sound(SOUND_GAME_OVER, volume=0) # Let arcade initialize sound so it doesn't freeze later

    startView = StartView()
    window.show_view(startView)

    arcade.run()

if __name__ == "__main__":
    import sys
    import os
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)
    main()