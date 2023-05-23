import pygame_gui
import pygame

from pygame import Color, Vector2
from utils import get_random_position, print_text_top, print_text, load_sprite
from models import Asteroid, Spaceship


class Asteroids:
    MIN_ASTEROID_DISTANCE = 250

    def __init__(self):
        self.init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 64)
        self.message = ""

        self.asteroids = []
        self.bullets = []
        self.spaceship = Spaceship((400, 300), self.bullets.append)

        for _ in range(6):
            while True:
                position = get_random_position(self.screen)
                if (
                        position.distance_to(self.spaceship.position)
                        > self.MIN_ASTEROID_DISTANCE
                ):
                    break

            self.asteroids.append(Asteroid(position, self.asteroids.append))

    def get_game_objects(self):
        game_objects = [*self.asteroids, *self.bullets]

        if self.spaceship:
            game_objects.append(self.spaceship)

        return game_objects

    def main_loop(self):
        while True:
            self.handle_input()
            self.process_game_logic()
            self.draw()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Asteroids")

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_game()
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
            if not is_key_pressed[pygame.K_UP]:
                self.spaceship.not_accelerate()

    def process_game_logic(self):
        for game_object in self.get_game_objects():
            game_object.move(self.screen)

        if self.spaceship:
            for asteroid in self.asteroids:
                if asteroid.collides_with(self.spaceship):
                    self.spaceship.position = (400, 300)
                    self.spaceship.lives -= 1
                    if self.spaceship.lives == 0:
                        self.spaceship = None
                        open_restart(self.screen)

        if self.spaceship:
            for bullet in self.bullets[:]:
                for asteroid in self.asteroids[:]:
                    if asteroid.collides_with(bullet):
                        self.asteroids.remove(asteroid)
                        self.bullets.remove(bullet)
                        asteroid.split(self.spaceship)
                        break

        for bullet in self.bullets[:]:
            if not self.screen.get_rect().collidepoint(bullet.position):
                self.bullets.remove(bullet)

        if not self.asteroids and self.spaceship:
            self.message = "You won!"

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.spaceship:
            heart_image = load_sprite("heart")
            heart_rect = heart_image.get_rect()
            for i in range(self.spaceship.lives):
                self.screen.blit(heart_image, (10 + i * heart_rect.width, 10))

            print_text_top(self.screen, f'Score: {self.spaceship.score}',
                           pygame.font.Font(None, 32))

        for game_object in self.get_game_objects():
            game_object.draw(self.screen)

        if self.message:
            print_text(self.screen, self.message, self.font)

        pygame.display.flip()
        self.clock.tick(60)

    def pause_game(self):
        pygame.display.set_caption("Paused")
        print_text(self.screen, "PAUSED", self.font)
        pygame.display.flip()
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.display.set_caption("Asteroids")
                        paused = False
                        break


def open_restart(surface):
    surface.fill((0, 0, 0))

    font_you_lose = pygame.font.Font(None, 100)
    text_you_lose = font_you_lose.render("You lose!", True, Color("red"))

    rect = text_you_lose.get_rect()
    rect.center = Vector2(surface.get_size()[0] // 2, 150)

    button_width = 200
    button_height = 100
    button_x = (surface.get_size()[0] - button_width) // 2
    button_y = (surface.get_size()[1] - button_height) // 2

    font = pygame.font.Font(None, 36)
    text = font.render("Restart", True, Color("white"))
    rect1 = text.get_rect()
    rect1.center = Vector2(button_x + (button_width - text.get_width()) // 2,
                           button_y + (button_height - text.get_height()) // 2)

    color_rectangle = (67, 67, 67)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            mouse_pos = pygame.mouse.get_pos()
            if button_x <= mouse_pos[0] <= button_x + button_width \
                    and button_y <= mouse_pos[1] <= button_y + button_height:
                color_rectangle = (82, 82, 82)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    restart_game()
            else:
                color_rectangle = (67, 67, 67)

        surface.fill(Color("black"))
        pygame.draw.rect(surface, color_rectangle,
                         (button_x, button_y, button_width, button_height))
        surface.blit(text, rect1)
        surface.blit(text_you_lose, rect)
        pygame.display.flip()


def restart_game():
    asteroids = Asteroids()
    asteroids.main_loop()
