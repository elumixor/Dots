import torch
import hyperparameters as hp
from ml.ai import AI
import game_ai as game
from random import random


def initialize():
    """
    Initializes environment
    :return:
    """

    return


def train(first: AI, second: AI, epochs=10, games_in_roll=10, win_factor=.9, discount_factor=0.5):
    """
    Trains models using self-play:
        repeat for epochs
            train first until it beats second
            train second until it beats first

    :param first:
    :param second:
    :param epochs:
    :param games_in_roll:
    :param win_factor:
    :param discount_factor:
    :return:
    """

    a, b = first, second

    a_learns = True

    for i in range(epochs):
        iterations = 0
        wp = 0
        roll = 0

        while wp < win_factor:
            won_games = 0
            roll += 1

            print(f"\tStarting roll {roll}")
            for i in range(games_in_roll):
                iterations += 1
                print(f"\tStarting game: {i}")

                result = game.start(a, b)
                if a_learns:
                    has_won = result == 0
                    reward = 1 if has_won else -1
                    a.learn(reward, discount_factor)
                else:
                    has_won = result == 1
                    reward = 1 if has_won else -1
                    b.learn(reward, discount_factor)

                if has_won:
                    won_games += 1

            wp = float(won_games) / games_in_roll
            print(f"\tRoll {roll}: {'A learns' if a_learns else 'B learns'}. Win Percent: {wp}. {win_factor} required")

        print(f"{'A' if a_learns else 'B'} (e {i}) took {iterations} games to beat {'B' if a_learns else 'A'}")
        a_learns = not a_learns


def test(first: AI, second: AI, number_of_games: int = 1):
    """

    :param first: first ai
    :param second: second ai
    :param number_of_games: number of games to be played
    """
    for i in range(number_of_games):
        game.start(first, second, True)


if __name__ == '__main__':
    torch.autograd.set_detect_anomaly(True)

    # Step 1: initialize environment
    a, b = AI.random(0), AI.random(1)
    # Step 2: train models
    train(a, b)
    # Step 3: test models (play some games), save games to files
    test(a, b, 25)
