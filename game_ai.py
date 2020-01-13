# start game
from file_logging import Log
from mechanics.board import Board, Point
from mechanics.common import min_value
from mechanics.grid import Grid
from hyperparameters import *
from ml.ai import AI
import numpy as np

grid: Grid = None
board: Board = None
current_player = 0


# game ends when there are no free points
def game_ended():
    for y in board_range:
        for x in board_range:
            group = board.points[y][x]

            if group is None and Point(x, y) not in board.captured_points:
                return False
    return True


def start(a: AI, b: AI, write_to_file=False):
    global grid
    global board
    global current_player

    grid = Grid(board_size, line_thickness, space_thickness, scale)
    board = Board(grid)

    a.board = b.board = board

    current_player = 0

    if write_to_file:
        log = Log()

    # play game
    while not game_ended():
        # make move for player in order
        a.make_move(0)

        if game_ended():
            if write_to_file:
                log.record(board)
            break

        b.make_move(1)

        # record board state
        if write_to_file:
            log.record(board)

    # save game log
    if write_to_file:
        log.save()

    # count point of each player and decide who is the winner
    player_points = [0 for _ in players]
    for y in board_range:
        for x in board_range:
            group = board.points[x][y]
            if group is not None and group.player != -1:
                player_points[group.player] += 1

    winner = np.argmax(np.array(player_points))

    print(f"\t\tGame ended: {['A', 'B'][winner]} has won")

    return winner
