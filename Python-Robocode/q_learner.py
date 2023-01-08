import math
from robot import Robot
import numpy as np
from random import choice


BUCKETS_NUM = 8

"""
possible actions:
move = [0, 1]
turn - [-1, 0, 1]
gunTurn - [-1, 0, 1]
fire - [0, 1] *power always 10
"""


class QLearner:
    def __init__(self, robot, epsilon):
        map_size = robot.getMapSize()
        map_size.width()
        # bounds for continuous parameters [map_x, map_y, bot_rotation, radar_rotation]
        self.upper_bounds = [map_size.width(), map_size.height(), 2*math.pi, 2*math.pi]
        self.lower_bounds = [0, 0, 0]
        self.observation_space = np.linspace(self.lower_bounds, self.upper_bounds, BUCKETS_NUM+1, endpoint=True, axis=1)
        self.action_space = [
            [0, 1],      # move
            [-1, 0, 1],  # turn
            [-1, 0, 1],  # gunTurn
            [0, 1],      # fire
        ]
        self.Q = {}
        self.epsilon = epsilon

    def learn(self, max_attempts):
        for _ in range(max_attempts):
            self.attempt()

    def attempt(self):
        # TODO: create learning mechanism
        reward = None
        return reward

    def discretise(self, observation):
        # observation should be [map_x, map_y, bot_rotation, radar_rotation, enemy detected]
        continuous_buckets = [np.digitize(x, self.observation_space[i]) for i, x in enumerate(observation[:-1])]
        return continuous_buckets + observation[-1]

    def pick_action(self, observation):
        if np.random.random() < self.epsilon:
            return self.random_action()
        else:
            # TODO: pick action from Q
            return None

    def update_knowledge(self, action, observation, new_observation, reward):
        # TODO: update Q
        pass

    def random_action(self):
        chosen_action = []
        for space_slice in self.action_space:
            chosen_action.append(choice(space_slice))
        return chosen_action


def main():
    pass


if __name__ == '__main__':
    main()
