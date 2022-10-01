import arcade

from src.consts import *
from src.vec import Vec2

class Player:
    def __init__(self, game, x, y):
        self.pos = Vec2(x, y)

        self.game = game

    def update(self, dt):
        dx = self.game.pressed[arcade.key.D] - self.game.pressed[arcade.key.A]
        dy = self.game.pressed[arcade.key.W] - self.game.pressed[arcade.key.S]
        delta = Vec2(dx, dy)
        delta.normalize()
        new = self.pos + delta * PLAYER_SPEED * dt
        half_size = PLAYER_SIZE / 2

        any_fix = False
        fix = Vec2(0, 0)
        for sx in (-half_size, half_size):
            for sy in (-half_size, half_size):
                if self.game.tile_at(new.x + sx, new.y + sy) != TILE_EMPTY:
                    fix -= (sx, sy)
                    any_fix = True
        if any_fix:
            delta += fix
            delta.normalize()
            new = self.pos + delta * PLAYER_SPEED * dt

        self.pos = new

    def draw(self):
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y, PLAYER_SIZE, PLAYER_SIZE, color=arcade.color.SAE)
