import arcade
from src.consts import *

def pointAABB(x, y, rectx, recty, width, height):
    return (rectx < x < rectx + width) and \
           (recty < y < recty + height)

class TextButton:
    def __init__(self, text, font_size, percentx, percenty, callback=None):
        self.percentx = percentx

        self.percenty = percenty
        self.callback = callback

        self.text = arcade.Text(
            text=text,
            start_x=0,
            start_y=0,
            color=arcade.color.WHITE,
            font_size=font_size,
            font_name=FONT,
            anchor_x='center',
            anchor_y='center'
        )

    def on_mouse_press(self, x, y):
        if pointAABB(x, y, self.text.left, self.text.bottom, *self.text.content_size):
            if self.callback:
                self.callback()

    def draw(self, window):
        x = window.width * self.percentx
        y = window.height * self.percenty

        self.text.x = x
        self.text.y = y

        self.text.draw()
        # self.text.draw_debug()