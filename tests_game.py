from unittest.mock import patch

import pygame

from unittest import TestCase, main, mock

from pygame import Vector2

from game import GameState, Asteroids, restart_game
from models import Spaceship, Asteroid, Bullet, Ufo

pygame.init()
pygame.display.set_mode((100, 100))


class TestAsteroids(TestCase):
    def setUp(self):
        self.asteroids_game = Asteroids()

    def test_constructor(self):
        self.assertEqual(self.asteroids_game.screen.get_size(), (1500, 700))
        self.assertIsInstance(self.asteroids_game.default_text_pos, Vector2)
        self.assertIsInstance(self.asteroids_game.default_button_pos, Vector2)
        self.assertIsInstance(self.asteroids_game.default_button_size, Vector2)
        self.assertIsInstance(self.asteroids_game.default_delay, Vector2)
        self.assertIsInstance(
            self.asteroids_game.default_input_field_size, Vector2
        )
        self.assertIsInstance(
            self.asteroids_game.default_input_field_rect_pos, tuple
        )
        self.assertIsInstance(self.asteroids_game.clock, pygame.time.Clock)
        self.assertEqual(self.asteroids_game.current_frame, 0)
        self.assertIsInstance(self.asteroids_game.font, pygame.font.Font)
        self.assertEqual(self.asteroids_game.nickname, "Default")
        self.assertTrue(self.asteroids_game.is_default_nickname)
        self.assertEqual(self.asteroids_game.level, 1)
        self.assertEqual(self.asteroids_game.ufo_quantity, 1)
        self.assertEqual(self.asteroids_game.game_state, GameState.MAIN_MENU)
        self.assertEqual(self.asteroids_game.bullets, [])
        self.assertEqual(self.asteroids_game.bullets_ufo, [])
        self.assertEqual(self.asteroids_game.ufo, [])
        self.assertEqual(
            self.asteroids_game.standard_spaceship_position,
            Vector2(1500 / 2, 700 / 2)
        )
        self.assertIsInstance(self.asteroids_game.spaceship, Spaceship)

    def test_handle_input_quit_event(self):
        event_quit = pygame.event.Event(pygame.QUIT)
        pygame.event.post(event_quit)

        self.asteroids_game._handle_input()

        self.assertEqual(self.asteroids_game.game_state, GameState.QUIT)

    def test_handle_input_escape_key(self):
        event_escape_key = pygame.event.Event(pygame.KEYDOWN,
                                              {"key": pygame.K_ESCAPE})
        pygame.event.post(event_escape_key)

        self.asteroids_game._handle_input()

        self.assertEqual(self.asteroids_game.game_state, GameState.PAUSE)

    def test_handle_input_space_key(self):
        event_space_key = pygame.event.Event(pygame.KEYDOWN,
                                             {"key": pygame.K_SPACE})
        pygame.event.post(event_space_key)

        with patch.object(Spaceship, 'shoot') as mock_shoot:
            self.asteroids_game._handle_input()

            mock_shoot.assert_called_once()

    def test_handle_input_arrow_keys(self):
        arrow_keys = [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP]
        for arrow_key in arrow_keys:
            event_arrow_key = pygame.event.Event(pygame.KEYDOWN,
                                                 {"key": arrow_key})
            pygame.event.post(event_arrow_key)

        self.asteroids_game._handle_input()

        self.assertEqual(self.asteroids_game.spaceship.direction,
                         pygame.math.Vector2(0, -1))
        self.assertEqual(self.asteroids_game.spaceship.velocity,
                         pygame.math.Vector2(0, 0))

        self.assertEqual(self.asteroids_game.spaceship.direction,
                         pygame.math.Vector2(0, -1))
        self.assertEqual(self.asteroids_game.spaceship.velocity,
                         pygame.math.Vector2(0, 0))

        self.assertEqual(self.asteroids_game.spaceship.direction,
                         pygame.math.Vector2(0, -1))
        self.assertEqual(self.asteroids_game.spaceship.velocity,
                         pygame.math.Vector2(0, 0))

    def test_handle_input_no_arrow_keys(self):
        self.asteroids_game.spaceship.direction = pygame.math.Vector2(0, -1)
        self.asteroids_game.spaceship.velocity = pygame.math.Vector2(0, 0)

        self.asteroids_game._handle_input()

        self.assertEqual(self.asteroids_game.spaceship.direction,
                         pygame.math.Vector2(0, -1))
        self.assertEqual(self.asteroids_game.spaceship.velocity,
                         pygame.math.Vector2(0, 0))

    def test_generate_enemies_level_1(self):
        asteroids_game = Asteroids()
        asteroids_game.level = 1

        with patch.object(Asteroids,
                          '_generate_asteroids') as mock_generate_asteroids:
            asteroids_game._generate_enemies()

            mock_generate_asteroids.assert_called_once_with(1)
            self.assertEqual(asteroids_game.ufo_quantity, 1)

    def test_generate_enemies_level_2(self):
        asteroids_game = Asteroids()
        asteroids_game.level = 2

        with patch.object(Asteroids,
                          '_generate_asteroids') as mock_generate_asteroids:
            asteroids_game._generate_enemies()

            mock_generate_asteroids.assert_called_once_with(4)
            self.assertEqual(asteroids_game.ufo_quantity, 2)

    def test_generate_enemies_level_3(self):
        asteroids_game = Asteroids()
        asteroids_game.level = 3

        with patch.object(Asteroids,
                          '_generate_asteroids') as mock_generate_asteroids:
            asteroids_game._generate_enemies()

            mock_generate_asteroids.assert_called_once_with(6)
            self.assertEqual(asteroids_game.ufo_quantity, 3)

    def test_generate_asteroids(self):
        asteroids_game = Asteroids()
        asteroids_game.spaceship.position = (100, 100)
        asteroids_quantity = 3

        asteroids_game._generate_asteroids(asteroids_quantity)

        for asteroid in asteroids_game.asteroids:
            position = asteroid.position
            self.assertTrue(position.distance_to(
                asteroids_game.spaceship.position) >
                            asteroids_game.MIN_ASTEROID_DISTANCE)

        self.assertEqual(len(asteroids_game.asteroids), 4)

    def test_get_game_objects(self):
        asteroids_game = Asteroids()
        asteroids_game.asteroids = [Asteroid((100, 100), None, 1),
                                    Asteroid((200, 200), None, 2)]
        asteroids_game.bullets = [Bullet((300, 300), (1, 0), True),
                                  Bullet((400, 400), (1, 0), False)]
        asteroids_game.ufo = [Ufo((500, 500), (1, 1), None)]
        asteroids_game.bullets_ufo = [Bullet((600, 600), (1, 0), False)]
        asteroids_game.spaceship = Spaceship((700, 700), None)

        game_objects = asteroids_game._get_game_objects()

        self.assertEqual(len(game_objects), 7)
        self.assertIsInstance(game_objects[0], Asteroid)
        self.assertIsInstance(game_objects[1], Asteroid)
        self.assertIsInstance(game_objects[2], Bullet)
        self.assertIsInstance(game_objects[3], Bullet)
        self.assertIsInstance(game_objects[4], Ufo)
        self.assertIsInstance(game_objects[5], Bullet)
        self.assertIsInstance(game_objects[6], Spaceship)

    def test_check_spaceship_collision(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), None)
        asteroid = Asteroid((200, 200), None, 1)
        bullet_ufo = Bullet((300, 300), (1, 0), False)
        ufo = Ufo((400, 400), (1, 1), None)

        asteroids_game.spaceship = spaceship
        asteroids_game.asteroids = [asteroid]
        asteroids_game.bullets_ufo = [bullet_ufo]
        asteroids_game.ufo = [ufo]

        asteroids_game._check_spaceship_collision()

        self.assertEqual(spaceship.lives, 3)
        self.assertEqual(len(asteroids_game.asteroids), 1)
        self.assertEqual(len(asteroids_game.bullets_ufo), 1)
        self.assertEqual(len(asteroids_game.ufo), 1)

    def test_spaceship_wrecked_logic(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), None)
        asteroid = Asteroid((100, 100), None, 1)
        bullet = Bullet((100, 100), (1, 0), True)
        ufo = Ufo((200, 200), (1, 1), None)

        asteroids_game.spaceship = spaceship
        spaceship.lives = 3

        asteroids_game._spaceship_wrecked_logic(asteroid, True)
        self.assertEqual(spaceship.lives, 2)

        asteroids_game._spaceship_wrecked_logic(bullet, False)
        self.assertEqual(spaceship.lives, 2)

        asteroids_game._spaceship_wrecked_logic(ufo, True)
        self.assertEqual(spaceship.lives, 2)

    def test_process_bullets_logic(self):
        asteroids_game = Asteroids()
        bullet1 = Bullet((100, 100), (1, 0), True)
        bullet2 = Bullet((2000, 2000), (1, 0), True)
        asteroids_game.bullets = [bullet1, bullet2]

        asteroids_game._process_bullets_logic()

        self.assertEqual(len(asteroids_game.bullets), 1)
        self.assertIn(bullet1, asteroids_game.bullets)
        self.assertNotIn(bullet2, asteroids_game.bullets)

    def test_check_bullets_collision(self):
        asteroids_game = Asteroids()
        bullet1 = Bullet((100, 100), (1, 0), True)
        bullet2 = Bullet((200, 200), (1, 0), True)
        bullet_ufo1 = Bullet((100, 100), (1, 0), False)
        bullet_ufo2 = Bullet((300, 300), (1, 0), False)

        asteroids_game.bullets = [bullet1, bullet2]
        asteroids_game.bullets_ufo = [bullet_ufo1, bullet_ufo2]

        asteroids_game._check_bullets_collision()

        self.assertEqual(len(asteroids_game.bullets), 1)
        self.assertIn(bullet2, asteroids_game.bullets)
        self.assertNotIn(bullet1, asteroids_game.bullets)

        self.assertEqual(len(asteroids_game.bullets_ufo), 1)
        self.assertIn(bullet_ufo2, asteroids_game.bullets_ufo)
        self.assertNotIn(bullet_ufo1, asteroids_game.bullets_ufo)

    def test_check_ufo_collision(self):
        asteroids_game = Asteroids()
        ufo1 = Ufo((100, 100), (1, 0), None)
        ufo2 = Ufo((200, 200), (1, 0), None)
        bullet1 = Bullet((100, 100), (1, 0), True)
        bullet2 = Bullet((300, 300), (1, 0), True)

        asteroids_game.ufo = [ufo1, ufo2]
        asteroids_game.bullets = [bullet1, bullet2]

        asteroids_game._check_ufo_collision()

        self.assertEqual(len(asteroids_game.ufo), 1)
        self.assertIn(ufo2, asteroids_game.ufo)
        self.assertNotIn(ufo1, asteroids_game.ufo)

        self.assertEqual(len(asteroids_game.bullets), 1)
        self.assertIn(bullet2, asteroids_game.bullets)
        self.assertNotIn(bullet1, asteroids_game.bullets)

        self.assertEqual(asteroids_game.spaceship.score, 200)

    def test_check_asteroids_collision(self):
        asteroids_game = Asteroids()
        asteroid1 = Asteroid((0, 0), asteroids_game.asteroids.append, 3)
        asteroid2 = Asteroid((100, 100), asteroids_game.asteroids.append, 3)
        bullet1 = Bullet((100, 100), (1, 0), True)
        bullet2 = Bullet((300, 300), (1, 0), True)

        asteroids_game.asteroids = [asteroid1, asteroid2]
        asteroids_game.bullets = [bullet1, bullet2]

        asteroids_game._check_asteroids_collision()

        self.assertEqual(len(asteroids_game.asteroids), 1)
        self.assertIn(asteroid2, asteroids_game.asteroids)
        self.assertNotIn(asteroid1, asteroids_game.asteroids)

        self.assertEqual(len(asteroids_game.bullets), 1)
        self.assertIn(bullet2, asteroids_game.bullets)
        self.assertNotIn(bullet1, asteroids_game.bullets)

    def test_generate_ufo(self):
        asteroids_game = Asteroids()
        asteroids_game.current_frame = 180
        asteroids_game.ufo_quantity = 1

        asteroids_game._generate_ufo()

        self.assertEqual(len(asteroids_game.ufo), 1)
        ufo = asteroids_game.ufo[0]
        self.assertIsInstance(ufo, Ufo)
        self.assertEqual(ufo.create_bullet_callback,
                         asteroids_game.bullets_ufo.append)

    def test_generate_ufo_no_spawn(self):
        asteroids_game = Asteroids()
        asteroids_game.current_frame = 0
        asteroids_game.ufo_quantity = 1

        asteroids_game._generate_ufo()

        self.assertEqual(len(asteroids_game.ufo), 0)

    def test_generate_ufo_decrement_quantity(self):
        asteroids_game = Asteroids()
        asteroids_game.current_frame = 180
        asteroids_game.ufo_quantity = 2

        asteroids_game._generate_ufo()

        self.assertEqual(asteroids_game.ufo_quantity, 1)

    def test_process_ufo_logic(self):
        asteroids_game = Asteroids()
        ufo = Ufo((100, 100), (1, 0), asteroids_game.bullets_ufo.append)
        ufo.current_frame = 75
        asteroids_game.ufo = [ufo]

        asteroids_game._process_ufo_logic()

        self.assertEqual(len(asteroids_game.ufo), 1)
        self.assertEqual(len(asteroids_game.bullets_ufo), 1)
        self.assertEqual(asteroids_game.bullets_ufo[0].position, (100, 100))

    def test_process_ufo_logic_remove_ufo(self):
        asteroids_game = Asteroids()
        ufo = Ufo((2000, 100), (-1, 0), asteroids_game.bullets_ufo.append)
        ufo.current_frame = 60
        asteroids_game.ufo = [ufo]

        asteroids_game._process_ufo_logic()

        self.assertEqual(len(asteroids_game.ufo), 0)
        self.assertEqual(len(asteroids_game.bullets_ufo), 0)

    def test_process_ufo_logic_no_ufo(self):
        asteroids_game = Asteroids()
        asteroids_game.ufo = []

        asteroids_game._process_ufo_logic()

        self.assertEqual(len(asteroids_game.ufo), 0)
        self.assertEqual(len(asteroids_game.bullets_ufo), 0)

    def test_move_objects(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        asteroids_game.spaceship = spaceship

        asteroids_game._move_objects()

        self.assertEqual(spaceship.position, (100, 100))

    def test_check_death_no_lives(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        spaceship.lives = 0
        asteroids_game.spaceship = spaceship

        asteroids_game._check_death()

        self.assertFalse(spaceship.is_alive)

    def test_check_death_with_lives(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        spaceship.lives = 2
        asteroids_game.spaceship = spaceship

        asteroids_game._check_death()

        self.assertTrue(spaceship.is_alive)

    def test_record_score_new_player(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        spaceship.score = 1000
        asteroids_game.spaceship = spaceship
        asteroids_game.nickname = "Player1"
        asteroids_game.leaderboard = {}

        asteroids_game._record_score()

        self.assertEqual(asteroids_game.leaderboard["Player1"], 1000)

    def test_record_score_higher_score(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        spaceship.score = 2000
        asteroids_game.spaceship = spaceship
        asteroids_game.nickname = "Player1"
        asteroids_game.leaderboard = {"Player1": 1500}

        asteroids_game._record_score()

        self.assertEqual(asteroids_game.leaderboard["Player1"], 2000)

    def test_record_score_lower_score(self):
        asteroids_game = Asteroids()
        spaceship = Spaceship((100, 100), asteroids_game.bullets.append)
        spaceship.score = 800
        asteroids_game.spaceship = spaceship
        asteroids_game.nickname = "Player1"
        asteroids_game.leaderboard = {"Player1": 1000}

        asteroids_game._record_score()

        self.assertEqual(asteroids_game.leaderboard["Player1"], 1000)

    def test_fill_leaderboard(self):
        asteroids_game = Asteroids()
        asteroids_game.leaderboard = {}

        asteroids_game._fill_leaderboard()

        expected_leaderboard = {"Player1": 1000}
        self.assertEqual(asteroids_game.leaderboard, expected_leaderboard)

    def test_check_game_state_spaceship_dead(self):
        asteroids_game = Asteroids()
        asteroids_game.spaceship.is_alive = False
        asteroids_game.game_state = GameState.GAME

        asteroids_game._check_game_state()

        expected_game_state = GameState.LOSE_MENU
        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_check_game_state_level_completed(self):
        asteroids_game = Asteroids()
        asteroids_game.spaceship.is_alive = True
        asteroids_game.asteroids = []
        asteroids_game.ufo = []
        asteroids_game.level = 3
        asteroids_game.game_state = GameState.WIN_MENU

        asteroids_game._check_game_state()

        expected_game_state = GameState.WIN_MENU
        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_check_game_state_level_not_completed(self):
        asteroids_game = Asteroids()
        asteroids_game.spaceship.is_alive = True
        asteroids_game.asteroids = []
        asteroids_game.ufo = []
        asteroids_game.level = 2
        asteroids_game.game_state = GameState.GAME

        asteroids_game._check_game_state()

        expected_game_state = GameState.GAME
        expected_spaceship_position = \
            asteroids_game.standard_spaceship_position
        expected_spaceship_direction = Vector2(0, -1)
        expected_bullets = []
        expected_bullets_ufo = []
        expected_level = 3

        self.assertEqual(asteroids_game.game_state, expected_game_state)
        self.assertEqual(asteroids_game.spaceship.position,
                         expected_spaceship_position)
        self.assertEqual(asteroids_game.spaceship.direction,
                         expected_spaceship_direction)
        self.assertEqual(asteroids_game.bullets, expected_bullets)
        self.assertEqual(asteroids_game.bullets_ufo, expected_bullets_ufo)
        self.assertEqual(asteroids_game.level, expected_level)

    def test_change_game_state_main_menu(self):
        asteroids_game = Asteroids()
        asteroids_game.game_state = GameState.GAME
        asteroids_game.nickname = "Player1"

        asteroids_game._change_game_state(GameState.MAIN_MENU)

        expected_game_state = GameState.MAIN_MENU

        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_change_game_state_game_with_nickname(self):
        asteroids_game = Asteroids()
        asteroids_game.game_state = GameState.MAIN_MENU
        asteroids_game.nickname = "Player1"

        asteroids_game._change_game_state(GameState.GAME)

        expected_game_state = GameState.GAME

        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_change_game_state_game_without_nickname(self):
        asteroids_game = Asteroids()
        asteroids_game.game_state = GameState.MAIN_MENU
        asteroids_game.nickname = ""

        asteroids_game._change_game_state(GameState.GAME)

        expected_game_state = GameState.MAIN_MENU

        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_change_game_state_other_state(self):
        asteroids_game = Asteroids()
        asteroids_game.game_state = GameState.MAIN_MENU

        asteroids_game._change_game_state(GameState.LEADERBOARD)

        expected_game_state = GameState.LEADERBOARD

        self.assertEqual(asteroids_game.game_state, expected_game_state)

    def test_restart_game_to_menu(self):
        asteroids_game = Asteroids()
        asteroids_game.nickname = "Player1"
        asteroids_game.game_state = GameState.GAME

        restart_game(asteroids_game, True)

        expected_game_state = GameState.MAIN_MENU
        expected_nickname = "Default"

        self.assertEqual(asteroids_game.game_state, expected_game_state)
        self.assertEqual(asteroids_game.nickname, expected_nickname)

    def test_restart_game_to_game(self):
        asteroids_game = Asteroids()
        asteroids_game.nickname = "Player1"
        asteroids_game.game_state = GameState.MAIN_MENU

        restart_game(asteroids_game, False)

        expected_game_state = GameState.GAME
        expected_nickname = "Player1"

        self.assertEqual(asteroids_game.game_state, expected_game_state)
        self.assertEqual(asteroids_game.nickname, expected_nickname)


if __name__ == '__main__':
    main()
