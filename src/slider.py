import arcade
import math

class Slider:
    def __init__(self, percent_x, percent_y, percent_width=0.2, value=0, low=0, high=1):
        self.percent_x = percent_x
        self.percent_y = percent_y
        self.percent_width = percent_width

        self.value = value
        self.low = low
        self.high = high

        self.mouse_is_holding = False

        self.center_x = 0
        self.center_y = 0
        self.width = 0
        self.start_x = 0
        self.end_x = 0
        self.slider_x = 0

    def get_value(self):
        ## map to range
        return self.low + self.value * (self.high - self.low)

    def update(self, window):
        self.center_x = window.width * self.percent_x
        self.center_y = window.height * self.percent_y
        self.width = window.width * self.percent_width
        self.start_x = self.center_x - self.width/2
        self.end_x = self.center_x + self.width/2

        self.slider_x = self.start_x * (1 - self.value) + self.end_x * self.value

    def on_mouse_press(self, x, y):
        if math.hypot(self.slider_x - x, self.center_y - y) < 10:
            self.mouse_is_holding = True

    def on_mouse_release(self, x, y):
        self.mouse_is_holding = False

    def on_mouse_drag(self, x, y, dx, dy):
        if not self.mouse_is_holding:
            return

        new_value = self.value + dx/self.width
        new_value = min(max(0, new_value), 1.0)
        self.value = new_value

    def draw(self):
        arcade.draw_line(
            start_x=self.start_x,
            start_y=self.center_y,
            end_x=self.end_x,
            end_y=self.center_y,
            color=arcade.color.GRAY,
            line_width=5
        )

        arcade.draw_circle_filled(
            center_x=self.slider_x,
            center_y=self.center_y,
            radius=10,
            color=arcade.color.GRAY_BLUE
        )