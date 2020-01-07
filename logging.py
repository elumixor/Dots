import os
from datetime import datetime

from mechanics.board import Board
from mechanics.parameters import *


class Log:
    # array of state
    # each state is an array of board points and players, e.g. points[y][x] = player
    states = []
    points = [[-1 for x in board_range] for y in board_range]

    # records current state on the board
    def record(self, board: Board):
        for y in board_range:
            for x in board_range:
                group = board.points[y][x]
                if group is None:
                    self.points[y][x] = -1
                    continue
                else:
                    self.points[y][x] = group.player

        self.states.append(str(self.points))

    def save(self):
        time = datetime.now()
        file_name = log_path + str(time)
        file = open(file_name, 'w')

        file.write(f"number_of_players={number_of_players}")
        file.write(f"board_size={board_size}")
        file.write(f"total_turns={len(self.states)}")

        file.writelines([state for state in self.states])
