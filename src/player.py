import math
import arcade

from src import ctx
from src.consts import *
from src.vec import Vec2
from src.utils import clamp

class Entity:
    def move_and_collide(self, delta: Vec2):
        current_tile = Vec2(*ctx.game.grid.tile_quantize(*self.pos))
        new = self.pos.copy()
        half_size = PLAYER_SIZE / 2

        for axis in range(2):
            new[axis] += delta[axis]
            any_fix = False
            for sx in (-half_size, half_size):
                for sy in (-half_size, half_size):
                    if ctx.game.grid.tile_at(new.x + sx, new.y + sy) != TILE_EMPTY:
                        any_fix = True
            if any_fix:
                eps = 0.001
                new[axis] = clamp(new[axis], current_tile[axis] + half_size + eps, current_tile[axis] + GRID_SCALE - half_size - eps)

        self.pos = new

class Player(Entity):
    SIZE = PLAYER_SIZE
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.last_tile = (-1, -1)

    def recompute_paths(self):
        ctx.game.pathFindingMap.compute([(self.last_tile.x // GRID_SCALE, self.last_tile.y // GRID_SCALE)])

    def update(self, dt):
        current_tile = Vec2(*ctx.game.grid.tile_quantize(*self.pos))
        if current_tile != self.last_tile:
            self.last_tile = current_tile
            self.recompute_paths()

        dx = ctx.game.pressed[arcade.key.RIGHT] - ctx.game.pressed[arcade.key.LEFT]
        dy = ctx.game.pressed[arcade.key.UP] - ctx.game.pressed[arcade.key.DOWN]

        if ctx.keyboard == 'qwerty':
            dx += ctx.game.pressed[arcade.key.D] - ctx.game.pressed[arcade.key.A]
            dy += ctx.game.pressed[arcade.key.W] - ctx.game.pressed[arcade.key.S]
        elif ctx.keyboard == 'azerty':
            dx += ctx.game.pressed[arcade.key.D] - ctx.game.pressed[arcade.key.Q]
            dy += ctx.game.pressed[arcade.key.Z] - ctx.game.pressed[arcade.key.S]

        dx = clamp(dx, -1, 1)
        dy = clamp(dy, -1, 1)

        delta = Vec2(dx, dy)
        delta.normalize()
        self.move_and_collide(delta * PLAYER_SPEED * dt)

    def draw(self):
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y, PLAYER_SIZE, PLAYER_SIZE, color=arcade.color.SAE)
