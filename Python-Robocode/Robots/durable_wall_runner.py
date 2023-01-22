import math
from robot import Robot
from durable.lang import *
from math import sqrt
from random import random

POINT_BLANK = 200
MOVE_STEP = 5
WALL_DISTANCE = 50
BULLET_POWER = 2

STATE_MOVING_UNKNOWN_DIRECTION = 0
STATE_MOVING_UP = 1
STATE_MOVING_RIGHT = 2
STATE_MOVING_DOWN = 3
STATE_MOVING_LEFT = 4


class WallRunnerDurable(Robot):

    def init(self):
        self.setColor(180, 180, 180)
        self.setGunColor(200, 200, 200)
        self.setRadarColor(200, 100, 0)
        self.setBulletsColor(255, 255, 230)

        self.radarVisible(True)

        self.areaSize = self.getMapSize()

        self.lockRadar("gun")
        self.setRadarField("thin")

        self.state = 'down'
        self.health = 100

        self.down_lim = self.areaSize.height() - WALL_DISTANCE
        self.left_lim = WALL_DISTANCE
        self.up_lim = WALL_DISTANCE
        self.right_lim = self.areaSize.width() - WALL_DISTANCE

        ruleset_seed = str(random())
        self.run_ruleset = 'run' + ruleset_seed
        self.rotate_ruleset = 'rotate' + ruleset_seed
        self.fire_ruleset = 'fire' + ruleset_seed

        self.init_ruleset()

        self.counter = 0

    def init_ruleset(self):
        with ruleset(self.run_ruleset):
            @when_all((m.state == 'down'))
            def down(c):
                y = self.getPosition().y()
                assert_fact(self.rotate_ruleset, {'state': c.m.state, 'yes': str(y > self.down_lim), 'r': self.get_counter()})

            @when_all((m.state == 'left'))
            def left(c):
                x = self.getPosition().x()
                assert_fact(self.rotate_ruleset, {'state': c.m.state, 'yes': str(x < self.left_lim), 'r': self.get_counter()})

            @when_all((m.state == 'up'))
            def up(c):
                y = self.getPosition().y()
                assert_fact(self.rotate_ruleset, {'state': c.m.state, 'yes': str(y < self.up_lim), 'r': self.get_counter()})

            @when_all((m.state == 'right'))
            def right(c):
                x = self.getPosition().x()
                assert_fact(self.rotate_ruleset, {'state': c.m.state, 'yes': str(x > self.right_lim), 'r': self.get_counter()})

        with ruleset(self.rotate_ruleset):
            @when_all((m.state == 'down') & (m.yes == 'True'))
            def down_rotate(c):
                self.stop()
                self.quarter_turn()
                self.state = 'left'

            @when_all((m.state == 'down') & (m.yes == 'False'))
            def down_continue(c):
                self.move(MOVE_STEP)

            @when_all((m.state == 'left') & (m.yes == 'True'))
            def left_rotate(c):
                self.stop()
                self.quarter_turn()
                self.state = 'up'

            @when_all((m.state == 'left') & (m.yes == 'False'))
            def left_continue(c):
                self.move(MOVE_STEP)

            @when_all((m.state == 'up') & (m.yes == 'True'))
            def up_rotate(c):
                self.stop()
                self.quarter_turn()
                self.state = 'right'

            @when_all((m.state == 'up') & (m.yes == 'False'))
            def up_continue(c):
                self.move(MOVE_STEP)

            @when_all((m.state == 'right') & (m.yes == 'True'))
            def right_rotate(c):
                self.stop()
                self.quarter_turn()
                self.state = 'down'

            @when_all((m.state == 'right') & (m.yes == 'False'))
            def right_continue(c):
                self.move(MOVE_STEP)

        with ruleset(self.fire_ruleset):
            @when_all((m.point_blank == 'True'))
            def point_blank_shot(c):
                self.fire(3*BULLET_POWER)

            @when_all((m.point_blank == 'False'))
            def normal_shot(c):
                self.fire(BULLET_POWER)

    def get_counter(self):
        self.counter += 1
        return self.counter

    def my_turn(self, angle):
        self.turn(angle)
        self.gunTurn(angle)

    def quarter_turn(self):
        self.my_turn(90)

    def run(self):
        assert_fact(self.run_ruleset, {'state': self.state, 'r': self.get_counter()})

    def onHitWall(self):
        self.reset()
        self.move(-2 * MOVE_STEP)

    def sensors(self):
        pass

    def onRobotHit(self, robotId, robotName):
        pass

    def onHitByRobot(self, robotId, robotName):
        pass

    def onHitByBullet(self, bulletBotId, bulletBotName, bulletPower):
        pass

    def onBulletHit(self, botId, bulletId):
        pass

    def onBulletMiss(self, bulletId):
        pass

    def onRobotDeath(self):
        pass

    def onTargetSpotted(self, botId, botName, botPos):
        self_pos = self.getPosition()
        self_x = self_pos.x()
        self_y = self_pos.y()

        bot_x = botPos.x()
        bot_y = botPos.y()

        bot_dist = sqrt(abs(self_x - bot_x)**2 + abs(self_y - bot_y)**2)

        is_point_blank = bot_dist < POINT_BLANK

        assert_fact(self.fire_ruleset, {'point_blank': str(is_point_blank), 'r': self.get_counter()})
