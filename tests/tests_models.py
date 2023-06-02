import unittest
from unittest.mock import Mock

from models import GameObject, Spaceship
from pygame import Surface, Vector2
from utils import wrap_position


class TestModels(unittest.TestCase):
    def setUp(self):
        self.surface = Mock()
        self.sprite = Mock()
        self.velocity = Vector2(2, 2)
        self.obj = GameObject((50, 50), self.sprite, self.velocity)

    def test_draw(self):
        self.obj.draw(self.surface)
        self.surface.blit.assert_called_once_with(self.sprite,
                                                  Vector2(50 - self.obj.radius,
                                                          50 - self.obj.radius))

    def test_move_within_surface(self):
        self.obj.position = Vector2(50, 50)
        self.obj.move(self.surface)
        expected_position = Vector2(52, 52)
        self.assertEqual(self.obj.position, expected_position)

    def test_collides_with(self):
        other_obj = Mock()
        other_obj.position = Vector2(60, 60)
        self.obj.position = Vector2(50, 50)
        self.obj.radius = 10
        other_obj.radius = 10
        self.assertTrue(self.obj.collides_with(other_obj))

    def test_collides_with_no_collision(self):
        other_obj = Mock()
        other_obj.position = Vector2(200, 200)
        self.obj.position = Vector2(50, 50)
        self.obj.radius = 10
        other_obj.radius = 10
        self.assertFalse(self.obj.collides_with(other_obj))

    def test_collides_with_non_existing_object(self):
        other_obj = None
        with self.assertRaises(Exception):
            self.obj.collides_with(other_obj)


if __name__ == '__main__':
    unittest.main()
