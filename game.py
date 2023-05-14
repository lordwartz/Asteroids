import pygame

from models import GameObject
from utils import load_sprite

class Asteroids:
    def __init__(self):
        self.init_pygame()
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.spaceship = GameObject(
            (400, 300), load_sprite("spaceship"), (0, 0)
        )
        self.asteroid = GameObject(
            (400, 300), load_sprite("asteroid"), (1, 0)
        )

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

    def process_game_logic(self):
        self.spaceship.move()
        self.asteroid.move()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.spaceship.draw(self.screen)
        self.asteroid.draw(self.screen)
        pygame.display.flip()
        self.clock.tick(60)
