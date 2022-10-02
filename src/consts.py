import arcade

# bottom left of map is at (0, 0)
GRID_SCALE = 4
GRID_WIDTH = 32
GRID_HEIGHT = 18

TILE_EMPTY = 0
TILE_WALL = 1

PLAYER_SPEED = 15
PLAYER_SIZE = 1

COLOR_DARK = (0, 0, 0)
COLOR_BRIGHT = (200, 200, 200)

RAGE_DELAY = 10

SCORE_KILL = 10
SCORE_PER_SECOND = 100

FONT = "assets/BebasNeue-Regular.ttf"

SOUND_GAME_OVER = arcade.Sound(":resources:sounds/error4.wav")