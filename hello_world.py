from p5 import *

lines = 10
scale = 3

# 15 width in total
line_thickness = 2
space_thickness = 13

# window width (and height) in pixels
window_size = (lines * (line_thickness + space_thickness) + space_thickness) * scale

def setup():
    size(window_size, window_size)
    title("Dots")


def draw():
    pass


run()
