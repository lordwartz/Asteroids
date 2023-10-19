import random
import pygame
from pygame_widgets.button import Button
from pygame import Color, Vector2
from scripts.utils import get_random_position, print_text, load_sprite, \
    get_random_size, draw_buttons, load_sound
from scripts.models import Asteroid, Spaceship, Ufo, Bullet
from enum import Enum


class GameState(Enum):
    MAIN_MENU = 0,
    GAME = 1,
    PAUSE = 2
    WIN_MENU = 3,
    LOSE_MENU = 4,
    QUIT = 5,
    ENTER_NAME = 6,
    LEADERBOARD = 7


class Asteroids:
    __MIN_ASTEROID_DISTANCE = 250
    __MIN_UFO_DISTANCE = 250
    __FRAMERATE = 60

    def __init__(self):
        init_pygame()
        self.__screen = pygame.display.set_mode((1500, 700))
        self.__default_text_pos = Vector2(self.__screen.get_width() // 2,
                                          self.__screen.get_height() // 12 * 6)
        self.__default_button_pos = Vector2(self.__screen.get_width() // 2,
                                            self.__screen.get_height() // 12 * 7)
        self.__default_button_size = Vector2(300, 50)
        self.__default_delay = Vector2(0, self.__screen.get_height() // 12)
        self.__default_input_field_size = Vector2(800, 60)
        self.__default_input_field_rect_pos = (self.__default_text_pos
                                               - self.__default_delay // 2
                                               - self.__default_input_field_size
                                               // 2,
                                               self.__default_input_field_size)
        self.__clock = pygame.time.Clock()
        self.__current_frame = 0
        self.__font = pygame.font.Font(None, 64)
        self.nickname = "Default"
        self.__is_default_nickname = True
        self.__leaderboard = {}
        self.__level = 1
        self.__ufo_quantity = 0

        self.menu_music = load_sound("Menu_m")
        self.game_music = load_sound("Game_m")
        self.win_music = load_sound("Win_m")
        self.lose_music = load_sound("Lose_m")
        self.musics = [self.menu_music,
                       self.game_music,
                       self.lose_music,
                       self.win_music]
        self.game_state_music = {GameState.MAIN_MENU: self.menu_music,
                                 GameState.GAME: self.game_music,
                                 GameState.WIN_MENU: self.win_music,
                                 GameState.LOSE_MENU: self.lose_music,
                                 GameState.PAUSE: self.game_music,
                                 GameState.ENTER_NAME: self.lose_music,
                                 GameState.LEADERBOARD: self.lose_music}

        self.__game_state = GameState.MAIN_MENU
        self.__previous_game_state = GameState.PAUSE
        self.__asteroids = []
        self.__bullets = []
        self.__bullets_ufo = []
        self.__ufo = []
        self.__standard_spaceship_position = Vector2(
            self.__screen.get_width() / 2,
            self.__screen.get_height() / 2
        )
        self.__spaceship = Spaceship(self.__standard_spaceship_position,
                                     self.__bullets.append)
        self.__generate_enemies()
        self.__fill_leaderboard("record_table.txt")

    def start_game(self):
        while self.__game_state is not GameState.QUIT:
            if (self.__previous_game_state != self.__game_state
                    and (not (self.__previous_game_state is GameState.MAIN_MENU
                              and self.__game_state in [GameState.ENTER_NAME,
                                                        GameState.LEADERBOARD]))
                    and (not (self.__previous_game_state in
                              [GameState.ENTER_NAME, GameState.LEADERBOARD]
                              and self.__game_state is GameState.MAIN_MENU))
                    and (not (self.__previous_game_state is GameState.PAUSE
                              and self.__game_state is GameState.GAME
                              or self.__previous_game_state is GameState.GAME
                              and self.__game_state is GameState.PAUSE))):
                self.stop_all_music()
                self.__play_music()
            if (self.__previous_game_state is GameState.PAUSE
                    and self.__game_state is GameState.GAME):
                self.game_music.set_volume(1)
            if (self.__previous_game_state is GameState.GAME
                    and self.__game_state is GameState.PAUSE):
                self.__spaceship.stop_music()
                self.game_music.set_volume(0.2)
            if self.__previous_game_state != self.__game_state:
                self.__previous_game_state = self.__game_state

            match self.__game_state:
                case GameState.MAIN_MENU:
                    self.__show_main_menu()
                case GameState.ENTER_NAME:
                    self.__show_input_field()
                case GameState.LEADERBOARD:
                    self.__show_leaderboard()
                case GameState.GAME:
                    self.__handle_input()
                    self.__process_game_logic()
                    self.__draw()
                case GameState.PAUSE:
                    self.__pause_game()
                case GameState.WIN_MENU:
                    self.__record_score("record_table.txt")
                    self.__show_win_menu()
                case GameState.LOSE_MENU:
                    self.__record_score("record_table.txt")
                    self.__show_lose_menu()
        else:
            quit()

    def __handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.__game_state = GameState.QUIT
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.__game_state = GameState.PAUSE
                elif self.__spaceship.is_alive and event.key == pygame.K_SPACE:
                    self.__spaceship.shoot()

        is_key_pressed = pygame.key.get_pressed()

        if self.__spaceship.is_alive:
            if is_key_pressed[pygame.K_RIGHT]:
                self.__spaceship.rotate(clockwise=True)
            elif is_key_pressed[pygame.K_LEFT]:
                self.__spaceship.rotate(clockwise=False)
            else:
                self.__spaceship.stop_rotating()
            if is_key_pressed[pygame.K_UP]:
                self.__spaceship.accelerate()
            else:
                self.__spaceship.not_accelerate()

    def __process_game_logic(self):
        self.__move_objects()
        self.__process_bullets_logic()
        if self.__ufo_quantity > 0:
            self.__generate_ufo()
        self.__process_ufo_logic()
        self.__check_bullets_collision()
        self.__check_ufo_collision()
        self.__check_asteroids_collision()
        self.__check_spaceship_collision()
        self.__check_game_state()

    def __draw(self):
        self.__screen.fill(Color("black"))
        pygame.display.set_caption("Asteroids")
        if self.__spaceship.is_alive:
            heart_image = load_sprite("heart")
            heart_rect = heart_image.get_rect()
            for i in range(self.__spaceship.lives):
                self.__screen.blit(heart_image,
                                   (10 + i * heart_rect.width, 10))

            print_text(self.__screen, f'Level {self.__level}',
                       pygame.font.Font(None, 28),
                       Vector2(48, 50), (150, 150, 150))
            print_text(self.__screen, f'Score: {self.__spaceship.score}',
                       pygame.font.Font(None, 32),
                       Vector2(self.__screen.get_size()[0] // 2, 20))
            print_text(self.__screen, self.nickname,
                       pygame.font.Font(None, 32),
                       Vector2(self.__screen.get_size()[0] // 2, 50),
                       (150, 150, 150))

        for game_object in self.__get_game_objects():
            game_object.draw(self.__screen)

        pygame.display.flip()
        self.__clock.tick(self.__FRAMERATE)
        self.__current_frame += 1

    def __generate_enemies(self):
        match self.__level:
            case 1:
                self.__generate_asteroids(1)
                self.__ufo_quantity = 1
            case 2:
                self.__generate_asteroids(4)
                self.__ufo_quantity = 2
            case 3:
                self.__generate_asteroids(6)
                self.__ufo_quantity = 3

    def __generate_asteroids(self, asteroids_quantity):
        for _ in range(asteroids_quantity):
            while True:
                position = get_random_position(self.__screen)
                if position.distance_to(self.__spaceship.position) \
                        > self.__MIN_ASTEROID_DISTANCE:
                    break

            self.__asteroids.append(Asteroid(position, self.__asteroids.append,
                                             get_random_size(0.8, 1.5)))

    def __get_game_objects(self):
        game_objects = [*self.__asteroids, *self.__bullets, *self.__ufo,
                        *self.__bullets_ufo]
        if self.__spaceship.is_alive:
            game_objects.append(self.__spaceship)

        return game_objects

    def __check_spaceship_collision(self):
        for asteroid in self.__asteroids[:]:
            self.__spaceship_wrecked_logic(asteroid, True)
        for bullet in self.__bullets_ufo[:]:
            self.__spaceship_wrecked_logic(bullet, False)
        for ufo in self.__ufo[:]:
            self.__spaceship_wrecked_logic(ufo, True)

    def __spaceship_wrecked_logic(self, collision_object, teleport):
        if self.__spaceship.is_alive \
                and collision_object.collides_with(self.__spaceship):
            if teleport:
                self.__spaceship.position = self.__standard_spaceship_position
            if type(collision_object) is Bullet:
                self.__bullets_ufo.remove(collision_object)
            self.__spaceship.lives -= 1
            self.__check_death()
            self.__spaceship.impact_sound.play()

    def __process_bullets_logic(self):
        for bullet in self.__bullets[:]:
            if not self.__screen.get_rect().collidepoint(bullet.position):
                self.__bullets.remove(bullet)

    def __check_bullets_collision(self):
        for bullet in self.__bullets[:]:
            for bullet_ufo in self.__bullets_ufo[:]:
                if bullet.collides_with(bullet_ufo):
                    self.__bullets.remove(bullet)
                    self.__bullets_ufo.remove(bullet_ufo)
                    break

    def __check_ufo_collision(self):
        for bullet in self.__bullets[:]:
            for ufo in self.__ufo[:]:
                if bullet.collides_with(ufo):
                    ufo.destroy()
                    self.__spaceship.score += 200
                    self.__ufo.remove(ufo)
                    self.__bullets.remove(bullet)
                    break

    def __check_asteroids_collision(self):
        for asteroid in self.__asteroids[:]:
            for bullet in self.__bullets[:]:
                if asteroid.collides_with(bullet):
                    self.__asteroids.remove(asteroid)
                    self.__bullets.remove(bullet)
                    asteroid.split(self.__spaceship)
                    break

    def __generate_ufo(self):
        directions = {0: (0, 1),
                      1: (1, 0),
                      2: (-1, 0),
                      3: (0, -1)}
        (random_x, random_y) = [random.randrange(self.__screen.get_width()),
                                random.randrange(self.__screen.get_height())]
        ufo_spawn = {(0, 1): (random_x, 0),
                     (1, 0): (0, random_y),
                     (-1, 0): (self.__screen.get_width() - 1, random_y),
                     (0, -1): (random_x, self.__screen.get_height() - 1)}
        if (self.__current_frame % (random.randrange(8, 12)
                                    * self.__FRAMERATE)) == self.__FRAMERATE * 3:
            direction = directions[random.randrange(4)]
            position = ufo_spawn[direction]
            self.__ufo.append(
                Ufo(position, direction, self.__bullets_ufo.append))
            self.__ufo_quantity -= 1

    def __process_ufo_logic(self):
        if self.__ufo:
            for ufo in self.__ufo[:]:
                if ufo.current_frame_alive % ufo.BULLET_FREQUENCY == 0:
                    ufo.shoot()
                if not self.__screen.get_rect().collidepoint(ufo.position):
                    self.__ufo.remove(ufo)

    def __move_objects(self):
        for game_object in self.__get_game_objects():
            game_object.move(self.__screen)

    def __check_death(self):
        if self.__spaceship.lives == 0:
            self.__spaceship.is_alive = False
            self.__spaceship.stop_music()
            for ufo in self.__ufo:
                ufo.stop_music()
            for asteroid in self.__asteroids:
                asteroid.stop_music()

    def __draw_label(self, text, color):
        print_text(self.__screen, text, self.__font,
                   self.__default_text_pos, color=color)

    def __show_main_menu(self):
        pygame.display.set_caption("Menu")
        self.__screen.fill(Color("black"))
        menu_buttons = [Button(self.__screen,
                               *(self.__default_button_pos
                                 - self.__default_button_size // 2),
                               *self.__default_button_size,
                               text='PLAY', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               radius=20,
                               onClick=lambda:
                               self.__change_game_state(GameState.ENTER_NAME)),
                        Button(self.__screen,
                               *(self.__default_button_pos
                                 + self.__default_delay
                                 - self.__default_button_size // 2),
                               *self.__default_button_size,
                               text='LEADERBOARD', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               radius=20,
                               onClick=lambda:
                               self.__change_game_state(
                                   GameState.LEADERBOARD))]
        while self.__game_state is GameState.MAIN_MENU:
            self.__draw_label("THE ASTEROIDS", "white")
            draw_buttons(menu_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                elif event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_TAB:
                            self.__game_state = GameState.LEADERBOARD

    def __pause_game(self):
        pygame.display.set_caption("Paused")
        buttons = [Button(self.__screen,
                          *(self.__default_button_pos -
                            self.__default_button_size // 2),
                          *self.__default_button_size,
                          text='MAIN MENU', fontSize=40,
                          inactiveColour=(155, 155, 155),
                          radius=20,
                          onClick=lambda:
                          self.__change_game_state(GameState.MAIN_MENU))]
        while self.__game_state is GameState.PAUSE:
            self.__draw_label("PAUSED", "red")
            draw_buttons(buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.set_caption("Asteroids")
                        self.__game_state = GameState.GAME
                        break

    def __show_input_field(self):
        pygame.display.set_caption("Enter your name")
        self.__screen.fill(Color("black"))
        buttons = [Button(self.__screen,
                          *(self.__default_button_pos -
                            self.__default_button_size // 2),
                          *self.__default_button_size,
                          text='START', fontSize=40,
                          inactiveColour=(255, 0, 0),
                          radius=20,
                          onClick=lambda:
                          self.__change_game_state(GameState.GAME)),
                   Button(self.__screen,
                          *(self.__default_button_pos
                            - self.__default_button_size // 2
                            + self.__default_delay),
                          *self.__default_button_size,
                          text='TO MENU', fontSize=40,
                          inactiveColour=(255, 0, 0),
                          radius=20,
                          onClick=lambda:
                          self.__change_game_state(GameState.MAIN_MENU))
                   ]
        while self.__game_state is GameState.ENTER_NAME:
            draw_buttons(buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.nickname = self.nickname[:-1]
                    elif event.key == pygame.K_RETURN:
                        self.__game_state = GameState.GAME
                        return
                    elif len(self.nickname) <= 20:
                        if self.__is_default_nickname:
                            self.nickname = ""
                            self.__is_default_nickname = False
                        self.nickname += event.unicode
            print_text(self.__screen, "Enter your name", self.__font,
                       self.__default_text_pos - self.__default_delay * 1.8,
                       Color("white"))
            pygame.draw.rect(self.__screen, (156, 156, 156),
                             self.__default_input_field_rect_pos)
            print_text(self.__screen, self.nickname, self.__font,
                       self.__default_text_pos - self.__default_delay // 2,
                       Color("white"))

    def __show_leaderboard(self):
        pygame.display.set_caption("Leaderboard")
        self.__screen.fill(Color("black"))
        menu_buttons = [Button(self.__screen,
                               *(self.__default_button_pos
                                 + self.__default_delay * 4
                                 - self.__default_button_size // 2),
                               *self.__default_button_size,
                               text='TO MENU', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               radius=20,
                               onClick=lambda:
                               self.__change_game_state(GameState.MAIN_MENU))]
        print_text(self.__screen, "Leaderboard", pygame.font.Font(None, 90),
                   (self.__screen.get_size()[0] // 2, self.__default_delay[1]),
                   Color("RED"))
        i = 1.5
        for player, score in self.__leaderboard.items():
            i += 1
            if i < 10:
                print_text(self.__screen, f"{player}: {score}", self.__font,
                           Vector2(self.__screen.get_size()[0] // 2,
                                   self.__default_delay[1] * i),
                           Color("white"))

        pygame.display.flip()

        while self.__game_state is GameState.LEADERBOARD:
            draw_buttons(menu_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_TAB:
                        self.__game_state = GameState.MAIN_MENU
                        return

    def __show_win_menu(self):
        pygame.display.set_caption("WIN")
        self.__screen.fill(Color("black"))
        win_buttons = [Button(self.__screen,
                              *(self.__default_button_pos -
                                self.__default_button_size // 2),
                              *self.__default_button_size,
                              text='RESTART', fontSize=40,
                              inactiveColour=(255, 0, 0),
                              radius=20,
                              onClick=lambda: restart_game(self, False)),
                       Button(self.__screen,
                              *(self.__default_button_pos
                                - self.__default_button_size // 2
                                + self.__default_delay),
                              *self.__default_button_size,
                              text='TO MENU', fontSize=40,
                              inactiveColour=(255, 0, 0),
                              radius=20,
                              onClick=lambda:
                              restart_game(self, True))
                       ]
        while self.__game_state is GameState.WIN_MENU:
            self.__draw_label("YOU WIN", "green")
            draw_buttons(win_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                    return

    def __show_lose_menu(self):
        pygame.display.set_caption("LOSE")
        self.__screen.fill(Color("black"))
        lose_buttons = [Button(self.__screen,
                               *(self.__default_button_pos -
                                 self.__default_button_size // 2),
                               *self.__default_button_size,
                               text='RESTART', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               radius=20,
                               onClick=lambda: restart_game(self, False)),
                        Button(self.__screen,
                               *(self.__default_button_pos
                                 - self.__default_button_size // 2
                                 + self.__default_delay),
                               *self.__default_button_size,
                               text='TO MENU', fontSize=40,
                               inactiveColour=(255, 0, 0),
                               radius=20,
                               onClick=lambda:
                               restart_game(self, True))
                        ]
        while self.__game_state is GameState.LOSE_MENU:
            self.__draw_label("YOU LOSE", "red")
            draw_buttons(lose_buttons)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.__game_state = GameState.QUIT
                    return

    def __record_score(self, filename):
        if self.nickname not in self.__leaderboard:
            self.__leaderboard[self.nickname] = self.__spaceship.score
        if self.__spaceship.score > self.__leaderboard[self.nickname]:
            self.__leaderboard[self.nickname] = self.__spaceship.score
        self.__leaderboard = dict(sorted(self.__leaderboard.items(),
                                         key=lambda item: item[1],
                                         reverse=True))
        with open(filename, "w") as record_table:
            for player, score in self.__leaderboard.items():
                record_table.write(f"{player}: {score} \n")

    def __fill_leaderboard(self, filename):
        with open(filename, "r") as record_table:
            for string in record_table:
                if not string.strip():
                    return
                player = string.split(":")[0]
                score = int(string.split(":")[1][1:])
                self.__leaderboard[player] = score

    def __check_game_state(self):
        if not self.__spaceship.is_alive:
            self.__game_state = GameState.LOSE_MENU
        elif not self.__asteroids and not self.__ufo and self.__level == 4:
            self.__game_state = GameState.WIN_MENU
        elif not self.__asteroids and not self.__ufo and self.__level < 4:
            self.__spaceship.position = self.__standard_spaceship_position
            self.__spaceship.direction = Vector2(0, -1)
            self.__bullets.clear()
            self.__bullets_ufo = []
            self.__level += 1
            self.__generate_enemies()

    def __change_game_state(self, game_state):
        match game_state:
            case GameState.MAIN_MENU:
                if self.__previous_game_state not in [GameState.ENTER_NAME,
                                                      GameState.LEADERBOARD]:
                    self.stop_all_music()
                    restart_game(self, True)
                else:
                    self.__game_state = GameState.MAIN_MENU
            case GameState.GAME:
                if len(self.nickname) > 0:
                    self.__game_state = GameState.GAME
            case _:
                self.__game_state = game_state

    def stop_all_music(self):
        for music in self.musics:
            music.stop()

    def __play_music(self):
        if self.__game_state not in [GameState.QUIT, GameState.ENTER_NAME,
                                     GameState.LEADERBOARD]:
            self.game_state_music[self.__game_state].play()
        if self.__game_state is GameState.PAUSE:
            self.game_state_music[self.__game_state].set_volume(0.35)


def init_pygame():
    pygame.init()
    pygame.display.set_caption("Asteroids")


def restart_game(asteroids, to_menu):
    nickname = asteroids.nickname
    asteroids.__init__()
    if not to_menu:
        asteroids.nickname = nickname
        asteroids.__game_state = GameState.GAME
    else:
        asteroids.__game_state = GameState.MAIN_MENU
