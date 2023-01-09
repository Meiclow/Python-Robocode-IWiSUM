
from robot import Robot #Import a base Robot


import math
import numpy as np
from random import choice
from collections import defaultdict


BUCKETS_NUM = 8
EPSILON = 0.1
ALPHA = 0.9
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
        self.lower_bounds = [0, 0, 0, 0]
        self.observation_space = np.linspace(self.lower_bounds, self.upper_bounds, BUCKETS_NUM+1, endpoint=True, axis=1)
        self.action_space = [
            [0, 1],      # move
            [-1, 0, 1],  # turn
            [-1, 0, 1],  # gunTurn
            [0, 1],      # fire
        ]
        self.Q = defaultdict(lambda: defaultdict(int))
        self.epsilon = epsilon

    def discretise(self, observation):
        # observation should be [map_x, map_y, bot_rotation, radar_rotation, enemy detected]
        continuous_buckets = [np.digitize(x, self.observation_space[i]) for i, x in enumerate(observation[:-1])]
        return continuous_buckets + observation[-1]

    def pick_action(self, observation):
        if np.random.random() < self.epsilon:
            return self.random_action()
        else:
            try:
                return max(self.Q[observation].items(), key = lambda x: x[1])[0]
            except ValueError as e:
                return self.random_action()

    def update_knowledge(self, action, observation, reward):
        self.Q[observation][action] = (1 - ALPHA) * self.Q[observation][action] + ALPHA * reward
        pass

    def random_action(self):
        return (choice(self.action_space[0]), choice(self.action_space[1]), 
                choice(self.action_space[2]), choice(self.action_space[3]))

class QLearningBot(Robot): #Create a Robot
    
    def init(self):# NECESARY FOR THE GAME   To initialyse your robot

        self.qlearner = QLearner(self, EPSILON)
        self.last_actions = []
        self.spotted = 0
        self.observation = (0,0,0,0,0)
        #Set the bot color in RGB
        self.setColor(0, 200, 100)
        self.setGunColor(200, 200, 0)
        self.setRadarColor(255, 60, 0)
        self.setBulletsColor(0, 200, 100)
        
        #get the map size
        size = self.getMapSize() #get the map size
        self.radarVisible(True) # show the radarField
        
    
    def run(self): #NECESARY FOR THE GAME  main loop to command the bot
        
        
        action = self.qlearner.pick_action(self.observation)
        self.last_actions.append(action)
        if len(self.last_actions) > 10:
            self.last_actions.pop(0)
        if action[0]:
            self.move(10)
        if action[1] == -1:
            self.turn(-10)
        elif action[1] == 1:
            self.turn(10)
        if action[2] == -1:
            self.gunTurn(-10)
            self.radarTurn(-10)
        elif action[2] == 1:
            self.gunTurn(10)
            self.radarTurn(10)
        if action[3]:
            self.fire(1)
            self.qlearner.update_knowledge(action, self.observation, -1)
        self.stop()
        self.spotted = 0

        
    def sensors(self):  #NECESARY FOR THE GAME
        """Tick each frame to have datas about the game"""
        self.observation = (self.getPosition().x(), self.getPosition().y(), self.getHeading(), self.getGunHeading(), self.spotted)
        
    def onHitByRobot(self, robotId, robotName):
        for action in self.last_actions:
            self.qlearner.update_knowledge(action, self.observation, -1)

    def onHitWall(self):
        pass
    
    def onRobotHit(self, robotId, robotName): # when My bot hit another
        for action in self.last_actions:
            self.qlearner.update_knowledge(action, self.observation, 2)
       
    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower): #NECESARY FOR THE GAME
        for action in self.last_actions:
            self.qlearner.update_knowledge(action, self.observation, -bulletPower)
        
    def onBulletHit(self, botId, bulletId):#NECESARY FOR THE GAME
        for action in self.last_actions:
            self.qlearner.update_knowledge(action, self.observation, 1)

        
    def onBulletMiss(self, bulletId):#NECESARY FOR THE GAME
        pass
        
    def onRobotDeath(self):#NECESARY FOR THE GAME
        pass
    
    def onTargetSpotted(self, botId, botName, botPos, _=None):#NECESARY FOR THE GAME
        self.spotted = 1
        pass
    
