import unittest
import math
import time

from src.simple_commander.controllers.main import GameController
from src.simple_commander.controllers.main import Bullet
from src.simple_commander.controllers.main import Hero
from src.simple_commander.controllers.main import Invader


class MainControllerTestCase(unittest.TestCase):
    def setUp(self):
        self.game_object = GameController(100, 100, 2)
        self.max_height = self.game_object.game_field['height']
        self.max_width = self.game_object.game_field['width']

    def test_game_field_width(self):
        self.assertEqual(self.game_object.game_field['width'], 100, 'incorrect game field width')

    def test_game_field_height(self):
        self.assertEqual(self.game_object.game_field['height'], 100, 'incorrect game field height')

    def test_game_field_units_length(self):
        self.assertEqual(len(self.game_object.units), 3, 'incorrect length of units')

    def test_bullet_create(self):
        self.game_object.fire(self.game_object.units[0])
        self.assertEqual(len(self.game_object.units), 4, 'Bullet was not created')

    def test_hero_start_speed(self):
        self.assertEqual(self.game_object.units[0].speed, 0, 'Incorrect initial speed')

    def test_hero_speed_after_change(self):
        self.game_object.units[0].change_speed(5)
        self.assertEqual(self.game_object.units[0].speed, 5, 'Incorrect initial speed')

    def test_hero_angle(self):
        hero = Hero(20, 20, 100)
        self.assertEqual(hero.angle, 100, 'Incorrect initial angle')

    def test_hero_angle_after_rotate(self):
        hero = Hero(20, 20, 100)
        hero.rotate(20)
        self.assertEqual(hero.angle, 120, 'Incorrect angle after rotate')

    #  Bullet coordinates after initial x = 0, y = 0, angle = 90:
    #    1. after 0 seconds --- step = 0, x = 0, y = 0
    #    2. after 1 seconds --- step = 1, x = -2, y = 0
    #    3. after 2 seconds --- step = 2, x = -4, y = -11
    #    4. after 3 seconds --- step = 3, x = -7, y = -31
    #  Coordinate will be the same as in invader!! Both units will be dead !!
    def test_compute_new_coordinate(self):
        hero = Hero(0, 0, 90)
        bullet = Bullet(hero)
        while bullet.step < 3:
            bullet.compute_new_coordinate(self.game_object.game_field)
        self.assertEqual(bullet.x, -7, 'Bullet coordinate x is incorrect!')
        self.assertEqual(bullet.y, -31, 'Bullet coordinate y is incorrect!')

    def test_check_collision_with_kill(self):
        hero = Hero(0, 0, 90)
        invader = Invader(-7, -31, 90, 10, 0)
        bullet = Bullet(hero)
        self.units = [hero, invader, bullet]
        while bullet.step < 3:
            bullet.compute_new_coordinate(self.game_object.game_field)
        bullet.check_collision(invader, self.units)
        self.assertEqual(bullet.is_dead, True, 'Bullet is not dead!')
        self.assertEqual(invader.is_dead, True, 'Invader is not dead!')
        self.assertEqual(hero.bonus, 10, 'Incorrect bonus for hero!')
        self.assertEqual(len(self.units), 1, 'Incorrect count of units after kill!!')

    def test_check_collision_without_kill(self):
        hero = Hero(0, 0, 90)
        invader = Invader(7, 31, 90, 10, 0)
        bullet = Bullet(hero)
        self.units = [hero, invader, bullet]
        while bullet.step < 3:
            bullet.compute_new_coordinate(self.game_object.game_field)
        bullet.check_collision(invader, self.units)
        self.assertEqual(bullet.is_dead, False, 'Bullet is dead!')
        self.assertEqual(invader.is_dead, False, 'Invader is dead!')
        self.assertEqual(hero.bonus, 0, 'Incorrect bonus for hero!')
        self.assertEqual(len(self.units), 3, 'Incorrect count of units after check collision!!')


if __name__ == '__main__':
    unittest.main()