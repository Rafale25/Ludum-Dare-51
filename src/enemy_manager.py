import math
from dataclasses import dataclass
import random
from numpy import mat

import pyglet
import arcade

from src import ctx
from src.consts import *
from src.vec import Vec2
from src.player import Entity
from src.utils import clamp

SPAWN_DELAY = 0.5
ENEMY_SPEED = 14

MAX_VEL = 0.8
TURNING_WEIGHT = 0.03

## acceleration structure
CELL_SIZE = PLAYER_SIZE

# @dataclass
class Enemy(Entity):
    def __init__(self, pos, batch):
        super().__init__()

        self.pos: Vec2 = pos
        self.vel: Vec2 = Vec2(0, 0)
        self.acc = Vec2(0, 0)
        self.dead: bool = False
        self.hash: int = 0
        self.shape = pyglet.shapes.Rectangle(self.pos.x, self.pos.y, PLAYER_SIZE, PLAYER_SIZE, color=arcade.color.CRIMSON, batch=batch)

class EnemyManager:
    def __init__(self):
        self.enemies = []
        self.until_spawn = -5
        self.until_rage = RAGE_DELAY
        self.rage_mode = False

        self.batch = pyglet.graphics.Batch()

        ## acceleration structure
        self.bucket = []
        self.count = []

    def cellCoord(self, x, y, size):
        return ( math.floor(x / size), math.floor(y/size) )

    def hashCoords(self, x, y, count):
        # h = y*675 + x
        h = y*(GRID_WIDTH*GRID_SCALE) + x
        return int(math.fabs(h)) % count

    def computeAccelerationStructure(self):
        n = len(self.enemies)
        self.count = [0] * (n+1)
        self.bucket = [None] * (n+1)

        for enemy in self.enemies:
            cell = self.cellCoord(enemy.pos.x, enemy.pos.y, CELL_SIZE)
            enemy.hash = self.hashCoords(cell[0], cell[1], n)

            self.count[enemy.hash] += 1

        # could use itertools.accumulate ot numpy.cumsum
        for i in range(1, n):
            self.count[i] += self.count[i - 1]

        for enemy in self.enemies:
            self.count[enemy.hash] -= 1
            self.bucket[ self.count[enemy.hash] ] = enemy

    def on_collision(self, enemy, player):
        if self.rage_mode:
            enemy.dead = True
            ctx.game.score += SCORE_KILL
            if ctx.game.alloc_sound():
                arcade.play_sound(random.choice(SOUNDS_KILL), volume=ctx.volume)
            ctx.game.blood_splashes.append(enemy.pos)
        else:
            ctx.game.end_game()

    def update(self, dt):
        if not self.rage_mode:
            self.until_spawn -= dt
        if self.until_spawn < 0:
            self.until_spawn += SPAWN_DELAY
            pos = random.choice([Vec2(x, y) for x in (2, (GRID_WIDTH-0.5) * GRID_SCALE) for y in (2, (GRID_HEIGHT-0.5) * GRID_SCALE)])
            self.enemies.append(Enemy(pos, self.batch)) # TODO select a better location
        self.until_rage -= dt
        if self.until_rage < 0:
            self.until_rage += RAGE_DELAY
            self.rage_mode = not self.rage_mode
            ctx.game.player.recompute_paths()

        self.computeAccelerationStructure()

        self.update_movement(dt)
        self.enemies[:] = [enemy for enemy in self.enemies if not enemy.dead]

    def compute_self_collision(self, me):
        n = len(self.enemies)

        for y in (-1, 0, 1):
            for x in (-1, 0, 1):
                cell = self.cellCoord(me.pos.x, me.pos.y, CELL_SIZE)

                cellHash = self.hashCoords(cell[0] + x, cell[1] + y, n)
                start = self.count[cellHash]

                end = self.count[cellHash + 1]

                for i in range(start, end):
                    if i >= n: break
                    other = self.bucket[i]
                    if me is other: continue

                    d = other.pos - me.pos

                    l = d.len()
                    if 0.0 < l < PLAYER_SIZE:
                        me.vel -= d.normalized() * (1.0/ (l*10.0) ) ## i tried something, not too bad


    def update_movement(self, dt):
        player = ctx.game.player
        for enemy in self.enemies:
            delta = player.pos - enemy.pos
            ln = delta.normalize()

            enemy_grid_x = int(enemy.pos.x / GRID_SCALE)
            enemy_grid_y = int(enemy.pos.y / GRID_SCALE)

            pathFindDir = Vec2(0.0, 0.0)

            if ctx.game.grid.isXYInGrid(enemy_grid_x, enemy_grid_y):
                pathFindDir = ctx.game.pathFindingMap.gradient[enemy_grid_y * GRID_WIDTH + enemy_grid_x]

            if self.rage_mode:
                delta *= -1

            direction = (delta*0.25 + pathFindDir).normalized()

            if self.rage_mode:
                if ln < GRID_SCALE * 6:
                    direction *= -1
                else:
                    direction *= -0.2

            prev_vel = enemy.vel.copy()
            enemy.vel += direction * TURNING_WEIGHT
            enemy.vel = enemy.vel.clamped(MAX_VEL)
            a = 0.9
            enemy.acc = enemy.acc * a + (enemy.vel-prev_vel) / dt * (1-a)

            self.compute_self_collision(enemy)

            enemy.move_and_collide(enemy.vel * ENEMY_SPEED * dt)

            if ln < PLAYER_SIZE:
                self.on_collision(enemy, player)

    def draw(self):
        for enemy in self.enemies:
            enemy.shape.x = enemy.pos.x - PLAYER_SIZE/2
            enemy.shape.y = enemy.pos.y - PLAYER_SIZE/2

            if ENABLE_STRETCH:
                mod = 0.1
                vec = enemy.acc
                cl = 0.25
                v = clamp(((abs(vec.x) - abs(vec.y)) * mod), -cl, cl)
                enemy.shape.width = PLAYER_SIZE * (1 + v)
                enemy.shape.height = PLAYER_SIZE * (1 - v)

        with arcade.get_window().ctx.pyglet_rendering():
            self.batch.draw()
