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
        try:
            delta.normalize()
        except ZeroDivisionError:
            pass
        new = self.pos + delta * PLAYER_SPEED * dt
        half_size = PLAYER_SIZE / 2

        for sx in (-half_size, half_size):
            for sy in (-half_size, half_size):
                if self.game.tile_at(new.x + sx, new.y + sy) != TILE_EMPTY:
                    break
        else:
            self.pos = new

    def draw(self):
        arcade.draw_rectangle_filled(self.pos.x, self.pos.y, PLAYER_SIZE, PLAYER_SIZE, color=arcade.color.SAE)
