import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import torch.distributions

from hyperparameters import number_of_players, board_size, board_range
from mechanics.board import Board, Point


class AI(nn.Module):
    # todo: create AI object
    def __init__(self, player_number: int, board=None):
        super().__init__()

        # 1 input image channel, 6 output channels, 3x3 square convolution kernel
        self.player_number: int = player_number
        self.conv1 = nn.Conv2d(1, 6, 3)
        self.conv2 = nn.Conv2d(6, 16, 3)

        # an affine operation: y = Wx + b
        self.fc1 = nn.Linear(16 * 5 * 5, 120)  # 6*6 from image dimension
        self.fc2 = nn.Linear(120, board_size ** 2)

        # board reference
        # self.optimizer = optim.SGD(self.parameters(), lr=0.01)
        self.optimizer = optim.Adam(self.parameters(), lr=0.01)
        # array of open points. 1 if a point can be placed, else 0
        self._board: Board = None
        self._open_points = torch.ones(board_size, board_size)

        self.episodes = []

    @property
    def actions_count(self):
        return len(self.episodes)

    @property
    def board(self):
        return self._board

    @board.setter
    def board(self, b):
        self._board = b
        self._open_points = torch.ones(board_size, board_size)
        for (x, y, g) in b:
            self._open_points[y][x] = 1 if g is None else 0

    def forward(self, x):
        # Max pooling over a (2, 2) window
        x = F.relu(self.conv1(x))
        # If the size is a square you can only specify a single number
        x = F.max_pool2d(F.relu(self.conv2(x)), 2, 1)
        x = x.view(-1, self.num_flat_features(x))
        # print(x)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = (x - x.min()) / (x.max() - x.min())  # normalize
        x = self.filter_board(x)
        return x

    def filter_board(self, x):
        """
        Filter out impossible positions, normalize remaining probabilities
        :param x: input vector 
        :return: 
        """""
        # select probability of closed points
        with torch.no_grad():
            closed = x * (self._open_points.reshape(-1, board_size ** 2) - 1).abs()
            op = self._open_points.reshape(-1, board_size ** 2)
            m = closed.mean()

        # select probability of open points
        x = (x + m) * op.clone()
        x = x / x.sum()

        return x

    def num_flat_features(self, x):
        size = x.size()[1:]  # all dimensions except the batch dimension
        num_features = 1
        for s in size:
            num_features *= s
        return num_features

    @staticmethod
    def random(player_number: int, board: Board = None):
        return AI(player_number, board)

    def make_move(self, player: int):
        # convert board state to tensor
        inp = torch.full((1, 1, board_size, board_size), -1)

        # form input from the dots on the board
        for (x, y, g) in self._board:
            if g is not None:
                inp[0][0][y][x] = g.player
                self._open_points[y][x] = 0  # place is taken
            else:
                self._open_points[y][x] = 1 if Point(x, y) not in self._board.captured_points else 0

        out = self(inp)

        # create a distribution of actions
        m = torch.distributions.Categorical(out)
        # sample an action
        action = m.sample()
        # add (distribution, action) pair into as new episode
        self.episodes.append((m, action))

        # return the x and y coordinates of the placed dot
        x, y = int(action % board_size), int(action // board_size)
        self.board.place_dot(x, y, player)

    def learn(self, reward, discount_factor):
        self.train()
        # print("Learning")
        for (i, (m, action)) in enumerate(self.episodes):
            # print(f"episode: {i}")
            self.optimizer.zero_grad()
            discounted = reward * (discount_factor ** (self.actions_count - i))  # we only receive reward at last action
            loss = -m.log_prob(action) * discounted
            loss.backward(retain_graph=(True if i < self.actions_count - 1 else False))
            self.optimizer.step()

        self.episodes = []
        self.eval()
