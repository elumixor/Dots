# start game
from logging import Log
from mechanics.board import Board, Point
from mechanics.grid import Grid
from mechanics.parameters import *
from ml.ai import AI

grid: Grid = None
board: Board = None
current_player = 0

# list of competing AI
ai = []


# game ends when there are no free points
def game_ended():
    for y in board_range:
        for x in board_range:
            group = board.points[y][x]

            if group is None and Point(x, y) not in board.captured_points:
                return False
    return True


def start():
    global grid
    global board
    global current_player
    global ai

    ai = [AI.random() for i in players]
    grid = Grid(board_size, line_thickness, space_thickness, scale)
    board = Board(grid)

    current_player = 0

    log = Log()

    # play game
    while not game_ended():
        # make move for player in order
        ai[current_player % number_of_players].make_move(board)

        # record board state
        log.record(board)

    # save game log
    log.save()
