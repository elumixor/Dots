from ast import literal_eval

from p5 import *

from mechanics.common import get_mouse_down
from mechanics.grid import Grid
from mechanics.board import Point, Board
from hyperparameters import *

# Grid and Board
grid = Grid(board_size, line_thickness, space_thickness, scale)
board = Board(grid)

current_player = 0


def setup():
    size(*grid.size)
    title("Dots")
    # generate_random_dots()


def draw():
    global mouse_x, mouse_y

    background("white")
    board.render()

    hint_point = grid.map_from_mouse(mouse_x, mouse_y)
    board.render_point(*hint_point, current_player % number_of_players)

    if get_mouse_down():
        add_next_point(*hint_point)


def generate_random_dots():
    number_of_dots = round(random_uniform() * max_dots)
    for i in range(0, number_of_dots):
        generate_random_dot()


def add_next_point(x, y):
    global current_player

    success = board.place_dot(x, y, current_player % number_of_players)
    if success:
        current_player += 1

    return success


def generate_random_dot():
    global current_player

    success = False

    while not success:
        success = board.place_dot(*Point.random(current_player % number_of_players))
        current_player += 1


def key_pressed():
    global key
    global current_player

    if key == "d":
        generate_random_dot()
    elif key == "p":
        # for (i, player_roots) in enumerate(board.groups):
        #     print(f"{i}: {colors[i]}: {player_roots}")
        board.print()

    elif key == "i":
        x, y = literal_eval(input(f"Enter coordinates ({colors[current_player % number_of_players]}): "))
        board.place_dot(x, y, current_player % number_of_players)
        current_player += 1

    elif key == "I":
        board.place_dot(1, 1, 0)
        board.place_dot(2, 2, 0)
        board.place_dot(0, 2, 0)
        board.place_dot(1, 3, 0)
    else:
        pass


if __name__ == "__main__":
    # print(str(Group()))

    run()
