from math import sin, pi
import random
import time
from collections import defaultdict
from typing import List

import arcade
import opensimplex

from src.consts import *
from src.player import Player
from src.enemy_manager import EnemyManager
from src.dijsktra import PathFindingMap
from src.vec import Vec2
from src import ctx
from src.maze import Maze

from pathlib import Path

# from time import perf_counter

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Ludum Dare 51"

RATIO = SCREEN_WIDTH / SCREEN_HEIGHT

VIEWPORT_SCALE = 3
VIEWPORT_WIDTH = 8*GRID_SCALE * RATIO * VIEWPORT_SCALE
VIEWPORT_HEIGHT = 8*GRID_SCALE * VIEWPORT_SCALE

def recalc_viewport(window):
    new_height = SCREEN_WIDTH/window.aspect_ratio
    height_fix = (new_height - SCREEN_HEIGHT) / 2
    arcade.set_viewport(0, SCREEN_WIDTH, -height_fix, SCREEN_HEIGHT+height_fix)

class StartView(arcade.View):
    def __init__(self):
        super().__init__()

        self.time_start = time.time()
        self.program = self.window.ctx.program(
            vertex_shader=Path('assets/shaders/background.vs').read_text(),
            fragment_shader=Path('assets/shaders/background.fs').read_text()
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

        recalc_viewport(self.window)

        arcade.draw_text(
            text="Press SPACE to start !!",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
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

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)
        self.setup()

class GameOverView(arcade.View):
    def __init__(self, score):
        super().__init__()
        self.score = score

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()

        recalc_viewport(self.window)

        arcade.draw_text(
            text=f"Bruh, your score is {int(self.score)}",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
            start_x=SCREEN_WIDTH/2,
            start_y=SCREEN_HEIGHT/2 + 50,
            anchor_x="center",
            anchor_y="center",
            rotation=sin(time.time() * 3) * 10)

        arcade.draw_text(
            text="Press Space to restart",
            bold=True,
            font_size=42,
            font_name="Bebas Neue",
            start_x=SCREEN_WIDTH/2,
            start_y=SCREEN_HEIGHT/2 - 50,
            anchor_x="center",
            anchor_y="center",
            rotation=sin((time.time()+4.789) * 3) * 10)

    def on_key_press(self, key, key_modifiers):
        if key == arcade.key.SPACE:
            ctx.game = GameView()
            self.window.show_view(ctx.game)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)

class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.pressed = defaultdict(bool)
        arcade.set_background_color(arcade.color.AMAZON)

        self.camera_center = Vec2(0, 0)

        self.grid = Maze.generate(GRID_WIDTH//2 + 1, GRID_HEIGHT//2 + 1).to_grid()

        CENTER_HOLE_RADIUS = 1
        for y in range(-CENTER_HOLE_RADIUS, CENTER_HOLE_RADIUS+1):
            for x in range(-CENTER_HOLE_RADIUS, CENTER_HOLE_RADIUS+1):
                i = self.toI(GRID_WIDTH//2 + x, GRID_HEIGHT//2 + y)
                self.grid[i] = TILE_EMPTY

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

        ## blood
        self.blood_splashes: List[Vec2] = []
        RESOLUTION_PER_TILE = 64
        self.texture_blood = self.window.ctx.texture(size=(GRID_WIDTH*RESOLUTION_PER_TILE, GRID_HEIGHT*RESOLUTION_PER_TILE), components=4)
        self.fbo_blood = self.window.ctx.framebuffer(
            color_attachments=self.texture_blood
        )
        self.fbo_blood.clear((0, 100, 0, 255))
        self.quad_blood_splash = arcade.gl.geometry.quad_2d(size=(1, 1), pos=(0, 0))
        self.quad_blood = arcade.gl.geometry.quad_2d(size=(GRID_WIDTH*GRID_SCALE, GRID_HEIGHT*GRID_SCALE), pos=(0, 0))
        self.program_blood_splash = self.window.ctx.program(
            vertex_shader=Path('assets/shaders/blood_splash.vs').read_text(),
            fragment_shader=Path('assets/shaders/blood_splash.fs').read_text()
        )
        self.program_blood = self.window.ctx.program(
            vertex_shader=Path('assets/shaders/blood.vs').read_text(),
            fragment_shader=Path('assets/shaders/blood.fs').read_text()
        )

        self.partial_dt = 0
        self.score = 0
        self.sound_limit = 0

    def end_game(self):
        arcade.play_sound(SOUND_GAME_OVER, volume=VOLUME)
        self.window.show_view(GameOverView(self.score))

    def tile_quantize(self, x, y):
        return Vec2(int(x / GRID_SCALE) * GRID_SCALE, int(y / GRID_SCALE) * GRID_SCALE)

    def index_at(self, x, y):
        x /= GRID_SCALE
        y /= GRID_SCALE
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            return int(y) * GRID_WIDTH + int(x)
        else:
            return None

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

        self.window.ctx.screen.use()

        if self.enemy_manager.rage_mode:
            self.clear(COLOR_BRIGHT)
        else:
            self.clear(COLOR_DARK)


        # self.fbo_blood.use()
        # self.quad_blood_splash.render(program=self.program_blood_splash)

        # self.texture_blood.use(unit=0)
        # self.quad_blood

        # arcade.set_viewport(0, GRID_WIDTH*64 * 100, 0, GRID_HEIGHT*64 * 100)

        self.window.ctx.screen.use()

        # arcade.set_viewport(0, GRID_WIDTH*GRID_SCALE, 0, GRID_HEIGHT*GRID_SCALE)
        ratio = self.window.aspect_ratio
        arcade.set_viewport(
            left=self.camera_center.x - VIEWPORT_WIDTH/2,
            right=self.camera_center.x + VIEWPORT_WIDTH/2,
            bottom=self.camera_center.y - VIEWPORT_WIDTH/ratio/2,
            top=self.camera_center.y + VIEWPORT_WIDTH/ratio/2
        )

        if self.enemy_manager.rage_mode:
            self.shape_list_map_2.draw()
        else:
            self.shape_list_map_1.draw()

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

        ## draws dijsktra map
        if False:
            recalc_viewport(self.window)
            for i in range(GRID_HEIGHT * GRID_WIDTH):
                y = i // GRID_WIDTH
                x = i % GRID_WIDTH
                arcade.draw_text(str(self.pathFindingMap.dijkstra[i]),
                    start_x=x* (SCREEN_WIDTH/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
                    start_y=y* (SCREEN_WIDTH/(GRID_WIDTH*GRID_SCALE)) * GRID_SCALE + GRID_SCALE/2,
                    color=arcade.color.RED)

        time_factor = 1
        tm = (self.enemy_manager.until_rage + time_factor/2) % RAGE_DELAY

        recalc_viewport(self.window)
        if tm < time_factor:
            color = COLOR_BRIGHT if self.enemy_manager.rage_mode == (tm > time_factor/2) else COLOR_DARK
            border_width = sin((tm) / time_factor * pi) * min(SCREEN_HEIGHT, SCREEN_WIDTH)
            arcade.draw_rectangle_outline(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, color, border_width)

        arcade.draw_text(f"Score: {int(self.score)}", SCREEN_WIDTH/2, SCREEN_HEIGHT-20, color=arcade.color.SAE, anchor_x='center', anchor_y='center', font_name=FONT, font_size=16)

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

            self.camera_center = self.camera_center + (self.player.pos - self.camera_center) * 0.3

    def on_key_press(self, key, key_modifiers):
        self.pressed[key] = True

        if key == arcade.key.F11:
            self.window.set_fullscreen(
                True - self.window.fullscreen
            )

    def on_key_release(self, key, key_modifiers):
        self.pressed[key] = False

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)


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
    main()