import random
import pygame
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
        self.__check_spaceship_collision()
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

        if self.win_message:
            print_text(self.screen, self.win_message, self.font,
                       Vector2(self.screen.get_size()) / 2)

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

    def __check_spaceship_collision(self):
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

    def __pause_game(self):
        pygame.display.set_caption("Paused")
        print_text(self.screen, "PAUSED", self.font,
                   Vector2(self.screen.get_size()) / 2)
        pygame.display.flip()
        while self.game_state is GameState.PAUSE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            pygame.display.set_caption("Asteroids")
                            self.game_state = GameState.GAME
                            break

    def __show_main_menu(self):
        pygame.display.set_caption("Menu")
        print_text(self.screen, "THE ASTEROIDS", self.font,
                   Vector2(self.screen.get_size()) / 2)
        pygame.display.flip()
        while self.game_state is GameState.MAIN_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_RETURN:
                            self.game_state = GameState.GAME
                            pygame.display.set_caption("Asteroids")
                            break
                        case pygame.K_ESCAPE:
                            self.game_state = GameState.QUIT
                            return

    def __show_win_menu(self):
        surface = self.screen
        surface.fill((0, 0, 0))

        button_width = 200
        button_height = 100
        button_x = (surface.get_size()[0] - button_width) // 2
        button_y = (surface.get_size()[1] - button_height) // 2

        text_message_color = Color("green")
        color_rectangle = (67, 67, 67)
        while self.game_state is GameState.WIN_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return
                mouse_pos = pygame.mouse.get_pos()
                if button_x <= mouse_pos[0] <= button_x + button_width \
                        and button_y <= mouse_pos[1] \
                        <= button_y + button_height:
                    color_rectangle = (82, 82, 82)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        restart_game()
                else:
                    color_rectangle = (67, 67, 67)

            surface.fill(Color("black"))
            pygame.draw.rect(surface, color_rectangle,
                             (button_x, button_y, button_width, button_height))
            print_text(surface, "YOU WIN", pygame.font.Font(None, 100),
                       Vector2(surface.get_size()[0] // 2, 150),
                       text_message_color)
            print_text(surface, "Restart", pygame.font.Font(None, 36),
                       Vector2(button_x + button_width // 2,
                               button_y + button_height // 2), Color("white"))
            pygame.display.flip()

    def __show_lose_menu(self):
        surface = self.screen
        surface.fill((0, 0, 0))

        button_width = 200
        button_height = 100
        button_x = (surface.get_size()[0] - button_width) // 2
        button_y = (surface.get_size()[1] - button_height) // 2

        text_message_color = Color("red")
        color_rectangle = (67, 67, 67)
        while self.game_state is GameState.LOSE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = GameState.QUIT
                    return
                mouse_pos = pygame.mouse.get_pos()
                if button_x <= mouse_pos[0] <= button_x + button_width \
                        and button_y <= mouse_pos[1] \
                        <= button_y + button_height:
                    color_rectangle = (82, 82, 82)
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        restart_game()
                else:
                    color_rectangle = (67, 67, 67)

            surface.fill(Color("black"))
            pygame.draw.rect(surface, color_rectangle,
                             (button_x, button_y, button_width, button_height))
            print_text(surface, "YOU LOSE", pygame.font.Font(None, 100),
                       Vector2(surface.get_size()[0] // 2, 150),
                       text_message_color)
            print_text(surface, "Restart", pygame.font.Font(None, 36),
                       Vector2(button_x + button_width // 2,
                               button_y + button_height // 2), Color("white"))
            pygame.display.flip()

    def __check_game_state(self):
        if not self.spaceship:
            self.game_state = GameState.LOSE_MENU
        elif not self.asteroids:
            self.game_state = GameState.WIN_MENU


def init_pygame():
    pygame.init()
    pygame.display.set_caption("Asteroids")


def restart_game():
    asteroids = Asteroids()
    asteroids.game_state = GameState.GAME
