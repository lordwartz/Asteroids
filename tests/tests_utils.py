from pygame import Surface, Vector2
from scripts.utils import wrap_position, get_random_velocity, get_random_size, \
    get_random_position
from unittest import TestCase, main


class TestUtils(TestCase):
    def test_wrap_position_within_surface(self):
        position = (50, 60)
        surface = Surface((100, 100))
        expected_result = (50, 60)
        self.assertEqual(wrap_position(position, surface), expected_result)

    def test_wrap_position_outside_surface(self):
        position = (150, 160)
        surface = Surface((100, 100))
        expected_result = (50, 60)
        self.assertEqual(wrap_position(position, surface), expected_result)

    def test_wrap_position_negative_values(self):
        position = (-50, -60)
        surface = Surface((100, 100))
        expected_result = (50, 40)
        self.assertEqual(wrap_position(position, surface), expected_result)

    def test_get_random_position_within_surface(self):
        surface = Surface((200, 300))
        result = get_random_position(surface)
        self.assertTrue(0 <= result.x < surface.get_width())
        self.assertTrue(0 <= result.y < surface.get_height())

    def test_get_random_velocity_within_speed_range(self):
        min_speed = 5
        max_speed = 10
        velocity = get_random_velocity(min_speed, max_speed)
        self.assertGreaterEqual(velocity.length(), min_speed)
        self.assertLessEqual(velocity.length(), max_speed)

    def test_get_random_velocity_angle_range(self):
        min_speed = 5
        max_speed = 10
        velocity = get_random_velocity(min_speed, max_speed)
        angle = abs(velocity.angle_to(Vector2(1, 0)))
        self.assertGreaterEqual(angle, 0)
        self.assertLess(angle, 360)

    def test_get_random_size_within_range(self):
        min_size = 1
        max_size = 10
        size = get_random_size(min_size, max_size)
        self.assertGreaterEqual(size, min_size)
        self.assertLessEqual(size, max_size)

    def test_get_random_size_equal_min_max(self):
        min_size = 5
        max_size = 5
        size = get_random_size(min_size, max_size)
        self.assertEqual(size, min_size)

    def test_get_random_size_negative_range(self):
        min_size = -10
        max_size = -5
        size = get_random_size(min_size, max_size)
        self.assertGreaterEqual(size, min_size)
        self.assertLessEqual(size, max_size)

    def test_get_random_size_float_range(self):
        min_size = 0.5
        max_size = 1.5
        size = get_random_size(min_size, max_size)
        self.assertGreaterEqual(size, min_size)
        self.assertLessEqual(size, max_size)


if __name__ == '__main__':
    main()
