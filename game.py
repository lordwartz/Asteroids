import random
import pygame
from pygame_widgets import Mouse
from pygame_widgets.button import Button
from pygame import Color, Vector2
from utils import get_random_position, print_text, load_sprite, get_random_size
from models import Asteroid, Spaceship, Ufo
from enum import Enum


class GameState(Enum):
    MAIN_MENU = 0,
    GAME = 1,
    PAUSE = 2
    WIN_MENU = 3,
    LOSE_MENU = 4,
    QUIT = 5


class Asteroids:
    MIN_ASTEROID_DISTANCE = 250
    MIN_UFO_DISTANCE = 250
    FRAMERATE = 60

    def __init__(self):
        init_pygame()
        self.screen = pygame.display.set_mode((1500, 800))
        self.default_text_pos = Vector2(self.screen.get_width() // 2,
                                        self.screen.get_height() // 12 * 6)
        self.default_button_pos = Vector2(self.screen.get_width() // 2,
                                          self.screen.get_height() // 12 * 7)
        self.default_button_size = Vector2(200, 50)
        self.default_button_delay = Vector2(0, self.screen.get_height() // 12)
        self.clock = pygame.time.Clock()
        self.current_frame = 0
        self.font = pygame.font.Font(None, 64)
        self.win_message = ""

        self.game_state = GameState.MAIN_MENU
        self.asteroids = []
        self.bullets = []
        self.bullets_ufo = []
        self.ufo = []
        self.standard_spaceship_position = Vector2(
            self.screen.get_width() / 2,
            self.screen.get_height() / 2
        )
        self.spaceship = Spaceship(self.standard_spaceship_position,
                                   self.bullets.append)
        self.__generate_asteroids()

    def start_game(self):
        while self.game_state is not GameState.QUIT:
            match self.game_state:
                case GameState.MAIN_MENU:
                    self.__show_main_menu()
                case GameState.GAME:
                    self.__handle_input()
                    self.__process_game_logic()
                    self.__draw()
                case GameState.PAUSE:
                    self.__pause_game()
                case GameState.WIN_MENU:
                    self.__show_win_menu()
                case GameState.LOSE_MENU:
                    self.__show_lose_menu()
        else:
            quit()

    def __handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_state = GameState.QUIT
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = GameState.PAUSE
                    return
                elif self.spaceship and event.key == pygame.K_SPACE:
                    self.spaceship.shoot()

        is_key_pressed = pygame.key.get_pressed()

        if self.spaceship:
            if is_key_pressed[pygame.K_RIGHT]:
                self.spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.spaceship.rotate(clockwise=False)
            if is_key_pressed[pygame.K_UP]:
                self.spaceship.accelerate()
            else:
                self.spaceship.not_accelerate()

    def __process_game_logic(self):
        self.__move_objects()
        self.__process_bullets_logic()
        self.__process_ufo_logic()
        self.__check_ufo_collision()
        self.__check_asteroids_collision()
        self._check_spaceship_collision()
        self.__check_game_state()

    def __draw(self):
        self.screen.fill((0, 0, 0))

        if self.spaceship:
            heart_image = load_sprite("heart")
            heart_rect = heart_image.get_rect()
            for i in range(self.spaceship.lives):
                self.screen.blit(heart_image, (10 + i * heart_rect.width, 10))

            print_text(self.screen, f'Score: {self.spaceship.score}',
                       pygame.font.Font(None, 32),
                       Vector2(self.screen.get_size()[0] // 2, 20))

        for game_object in self.__get_game_objects():
            game_object.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(self.FRAMERATE)
        self.current_frame += 1

    def __generate_asteroids(self):
        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if position.distance_to(self.spaceship.position) \
                        > self.MIN_ASTEROID_DISTANCE:
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append,
                                           get_random_size(0.8, 1.5)))

    def __get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets, *self.ufo,
                        *self.bullets_ufo]
        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects

    def _check_spaceship_collision(self):
        for asteroid in self.asteroids[:]:
            if self.spaceship and asteroid.collides_with(self.spaceship):
                self.spaceship.position = self.standard_spaceship_position
                self.spaceship.lives -= 1
                self.__check_death()
        for bullet in self.bullets_ufo[:]:
            if self.spaceship and bullet.collides_with(self.spaceship):
                self.spaceship.lives -= 1
                self.__check_death()
                self.bullets_ufo.remove(bullet)
                break

    def __process_bullets_logic(self):
        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

    def __check_ufo_collision(self):
        for bullet in self.bullets[:]:
            for ufo in self.ufo[:]:
                if bullet.collides_with(ufo):
                    self.ufo.remove(ufo)
                    self.bullets.remove(bullet)

    def __check_asteroids_collision(self):
        for asteroid in self.asteroids[:]:
            for bullet in self.bullets[:]:
                if asteroid.collides_with(bullet):
                    self.asteroids.remove(asteroid)
                    self.bullets.remove(bullet)
                    asteroid.split(self.spaceship)
                    break

    def __process_ufo_logic(self):
        directions = {0: (0, 1),
                      1: (1, 0),
                      2: (-1, 0),
                      3: (0, -1)}
        (random_x, random_y) = [random.randrange(self.screen.get_width()),
                                random.randrange(self.screen.get_height())]
        ufo_spawn = {(0, 1): (random_x, 0),
                     (1, 0): (0, random_y),
                     (-1, 0): (self.screen.get_width() - 1, random_y),
                     (0, -1): (random_x, self.screen.get_height() - 1)}
        if (self.current_frame % (random.randrange(8, 12)
                                  * self.FRAMERATE)) == self.FRAMERATE * 4:
            direction = directions[random.randrange(4)]
            position = ufo_spawn[direction]
            self.ufo.append(Ufo(position, direction, self.bullets_ufo.append))

        if self.ufo:
            for ufo in self.ufo[:]:
                if ufo.current_frame % ufo.BULLET_FREQUENCY == 0:
                    ufo.shoot()
                if not self.screen.get_rect().collidepoint(ufo.position):
                    self.ufo.remove(ufo)

    def __move_objects(self):
        for game_object in self.__get_game_objects():
            game_object.move(self.screen)

    def __check_death(self):
        if self.spaceship.lives == 0:
            self.spaceship = None

    def __draw_label(self, text, color):
        print_text(self.screen, text, self.font,
                   self.default_text_pos, color=color)

    def __draw_buttons(self, lose_buttons):
        Mouse.updateMouseState()
        for button in lose_buttons:
            button.listen(pygame.event.get())
            button.draw()

    def __show_main_menu(self):
        pygame.display.set_caption("Menu")
        self.screen.fill((0, 0, 0))
        menu_buttons = [Button(self.screen,
                               *(self.default_button_pos
                                 - self.default_button_size // 2),
                               *self.default_button_size,
                               text='PLAY', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               pressedColour=(0, 255, 0), radius=20,
                               onClick=lambda:
                               self.__change_game_state(GameState.GAME))]
        while self.game_state is GameState.MAIN_MENU:
            self.__draw_label("THE ASTEROIDS", "white")
            self.__draw_buttons(menu_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT

    def __pause_game(self):
        pygame.display.set_caption("Paused")
        buttons = [Button(self.screen,
                          *(self.default_button_pos -
                            self.default_button_size // 2),
                          *self.default_button_size,
                          text='MAIN MENU', fontSize=40,
                          inactiveColour=(155, 155, 155),
                          pressedColour=(200, 200, 200), radius=20,
                          onClick=lambda:
                          self.__change_game_state(GameState.MAIN_MENU))]
        while self.game_state is GameState.PAUSE:
            self.__draw_label("PAUSED", "red")
            self.__draw_buttons(buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.set_caption("Asteroids")
                        self.game_state = GameState.GAME
                        break

    def __show_win_menu(self):
        pygame.display.set_caption("WIN")
        self.screen.fill((0, 0, 0))
        win_buttons = [Button(self.screen,
                              *(self.default_button_pos -
                                self.default_button_size // 2),
                              *self.default_button_size,
                              text='RESTART', fontSize=40,
                              inactiveColour=(255, 0, 0),
                              pressedColour=(0, 255, 0), radius=20,
                              onClick=lambda: restart_game(self, False)),
                       Button(self.screen,
                              *(self.default_button_pos
                                - self.default_button_size // 2
                                + self.default_button_delay),
                              *self.default_button_size,
                              text='TO MENU', fontSize=40,
                              inactiveColour=(255, 0, 0),
                              pressedColour=(0, 255, 0),
                              radius=20,
                              onClick=lambda:
                              restart_game(self, True))
                       ]
        while self.game_state is GameState.WIN_MENU:
            self.__draw_label("YOU WIN", "green")
            self.__draw_buttons(win_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return

    def __show_lose_menu(self):
        pygame.display.set_caption("LOSE")
        self.screen.fill((0, 0, 0))
        lose_buttons = [Button(self.screen,
                               *(self.default_button_pos -
                                 self.default_button_size // 2),
                               *self.default_button_size,
                               text='RESTART', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               pressedColour=(0, 255, 0), radius=20,
                               onClick=lambda: restart_game(self, False)),
                        Button(self.screen,
                               *(self.default_button_pos
                                 - self.default_button_size // 2
                                 + self.default_button_delay),
                               *self.default_button_size,
                               text='TO MENU', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               pressedColour=(0, 255, 0),
                               radius=20,
                               onClick=lambda:
                               restart_game(self, True))
                        ]
        while self.game_state is GameState.LOSE_MENU:
            self.__draw_label("YOU LOSE", "red")
            self.__draw_buttons(lose_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return

    def __check_game_state(self):
        if not self.spaceship:
            self.game_state = GameState.LOSE_MENU
        elif not self.asteroids:
            self.game_state = GameState.WIN_MENU

    def __change_game_state(self, game_state):
        if game_state is GameState.MAIN_MENU:
            restart_game(self, True)
        else:
            self.game_state = game_state


def init_pygame():
    pygame.init()
    pygame.display.set_caption("Asteroids")


def restart_game(asteroids, to_menu):
    asteroids.__init__()
    asteroids.game_state = GameState.MAIN_MENU if to_menu else GameState.GAME
