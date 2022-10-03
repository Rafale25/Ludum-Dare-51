import arcade

# bottom left of map is at (0, 0)
GRID_SCALE = 4
GRID_WIDTH = 33
GRID_HEIGHT = 19

TILE_EMPTY = 0
TILE_WALL = 1

PLAYER_SPEED = 15
PLAYER_SIZE = 1

COLOR_DARK = (0, 0, 0)
COLOR_BRIGHT = (120, 120, 120)
COLOR_BRIGHT_2 = (200, 200, 200)

RAGE_DELAY = 10

SCORE_KILL = 100
SCORE_PER_SECOND = 10

VOLUME = 0.2
FONT = "Bebas Neue"

SOUND_GAME_OVER = arcade.load_sound(":resources:sounds/error4.wav")
SOUNDS_KILL = [arcade.load_sound(f":resources:sounds/hit{i}.wav") for i in (1, 3, 5)]

ENABLE_STRETCH = False
