from unittest import TestCase, main
from unittest.mock import Mock

import pygame
from pygame import Surface, Vector2

from models import GameObject, Spaceship, Asteroid, Bullet, Ufo
from utils import wrap_position

pygame.init()
pygame.display.set_mode((100, 100))


class TestGameObject(TestCase):
    def setUp(self):
        self.surface = Surface((100, 100))
        self.sprite = Surface((20, 20))
        self.velocity = (2, 2)
        self.obj = GameObject((50, 50), self.sprite, self.velocity)

    def test_move_within_surface(self):
        initial_position = self.obj.position.copy()
        self.obj.move(self.surface)
        expected_position = wrap_position(initial_position + self.velocity,
                                          self.surface)
        self.assertEqual(self.obj.position, expected_position)

    def test_move_outside_surface(self):
        self.obj.position = Vector2(99, 99)
        initial_position = self.obj.position.copy()
        self.obj.move(self.surface)
        expected_position = wrap_position(initial_position + self.velocity,
                                          self.surface)
        self.assertEqual(self.obj.position, expected_position)

    def test_collides_with(self):
        other_obj = GameObject((60, 60), self.sprite, self.velocity)
        self.assertTrue(self.obj.collides_with(other_obj))

    def test_collides_with_no_collision(self):
        other_obj = GameObject((200, 200), self.sprite, self.velocity)
        self.assertFalse(self.obj.collides_with(other_obj))

    def test_collides_with_non_existing_object(self):
        other_obj = None
        with self.assertRaises(Exception):
            self.obj.collides_with(other_obj)


class TestSpaceship(TestCase):
    def setUp(self):
        self.create_bullet_callback = Mock()
        self.position = (50, 50)
        self.spaceship = Spaceship(self.position, self.create_bullet_callback)

    def test_add_score(self):
        initial_score = self.spaceship.score
        score_value = 10
        self.spaceship.add_score(score_value)
        self.assertEqual(self.spaceship.score, initial_score + score_value)

    def test_rotate_clockwise(self):
        initial_direction = self.spaceship.direction.copy()
        self.spaceship.rotate(clockwise=True)
        expected_direction = initial_direction.rotate(
            self.spaceship.MANEUVERABILITY)
        self.assertEqual(self.spaceship.direction, expected_direction)

    def test_rotate_counterclockwise(self):
        initial_direction = self.spaceship.direction.copy()
        self.spaceship.rotate(clockwise=False)
        expected_direction = initial_direction.rotate(
            -self.spaceship.MANEUVERABILITY)
        self.assertEqual(self.spaceship.direction, expected_direction)

    def test_accelerate(self):
        initial_velocity = self.spaceship.velocity.copy()
        self.spaceship.accelerate()
        expected_velocity = initial_velocity + self.spaceship.direction * self.spaceship.ACCELERATION
        self.assertEqual(self.spaceship.velocity, expected_velocity)

    def test_not_accelerate_with_velocity(self):
        self.spaceship.velocity = Vector2(2, 2)
        self.spaceship.not_accelerate()
        expected_velocity = Vector2(2, 2) - Vector2(2, 2) * self.spaceship.SPACESHIP_ANTIGRAVITY
        self.assertEqual(self.spaceship.velocity, expected_velocity)

    def test_not_accelerate_without_velocity(self):
        self.spaceship.velocity = Vector2(0, 0)
        self.spaceship.not_accelerate()
        self.assertEqual(self.spaceship.velocity, Vector2(0, 0))


class TestAsteroid(TestCase):
    def setUp(self):
        self.create_asteroid_callback = Mock()
        self.position = (50, 50)
        self.initial_size = 3
        self.asteroid = Asteroid(
            self.position, self.create_asteroid_callback,
            self.initial_size
        )

    def test_split(self):
        spaceship = Spaceship((50, 50), Mock())
        initial_score = spaceship.score
        self.asteroid.split(spaceship)
        expected_score = initial_score + {
            3: 25,
            2: 50,
            1: 100,
        }[self.asteroid.reduction_size]
        self.assertEqual(spaceship.score, expected_score)
        if self.asteroid.reduction_size > 1:
            self.assertEqual(self.create_asteroid_callback.call_count, 2)
            for call_args in self.create_asteroid_callback.call_args_list:
                asteroid = call_args[0][0]
                self.assertEqual(asteroid.position, self.asteroid.position)
                self.assertEqual(asteroid.create_asteroid_callback,
                                 self.create_asteroid_callback)
                self.assertEqual(asteroid.initial_size,
                                 self.asteroid.initial_size)
                self.assertEqual(asteroid.reduction_size,
                                 self.asteroid.reduction_size - 1)
        else:
            self.assertEqual(self.create_asteroid_callback.call_count, 0)


class TestBullet(TestCase):
    def setUp(self):
        self.position = (50, 50)
        self.velocity = Vector2(1, 1)
        self.is_spaceship_bullet = True
        self.bullet = Bullet(self.position, self.velocity,
                             self.is_spaceship_bullet)

    def test_constructor(self):
        self.assertEqual(self.bullet.position, Vector2(self.position))
        self.assertEqual(self.bullet.velocity, self.velocity)

    def test_move(self):
        surface = Mock()
        self.bullet.move(surface)
        expected_position = self.position + self.velocity
        self.assertEqual(self.bullet.position, Vector2(expected_position))


class TestUfo(TestCase):
    def setUp(self):
        self.position = (50, 50)
        self.velocity = Vector2(1, 1)
        self.create_bullet_callback = Mock()
        self.ufo = Ufo(
            self.position, self.velocity, self.create_bullet_callback
        )

    def test_constructor(self):
        self.assertEqual(self.ufo.position, Vector2(self.position))
        self.assertEqual(self.ufo.velocity, self.velocity)
        self.assertEqual(self.ufo.current_frame, 0)

    def test_move(self):
        surface = Mock()
        self.ufo.move(surface)
        expected_position = self.position + self.velocity
        self.assertEqual(self.ufo.position, Vector2(expected_position))
        self.assertEqual(self.ufo.current_frame, 1)


if __name__ == '__main__':
    main()
