import random

from pygame import Color, event
from pygame.image import load
from pygame.math import Vector2
from pygame_widgets import Mouse
from pygame.mixer import Sound


def load_sprite(name, with_alpha=True):
    path = f"../assets/sprites/{name}.png"
    loaded_sprite = load(path)

    if with_alpha:
        return loaded_sprite.convert_alpha()
    else:
        return loaded_sprite.convert()


def load_sound(name)
    path = f"../assets/sounds/{name}.png"
    return Sound(path)

def wrap_position(position, surface):
    x, y = position
    w, h = surface.get_size()
    return Vector2(x % w, y % h)


def get_random_position(surface):
    return Vector2(
        random.randrange(surface.get_width()),
        random.randrange(surface.get_height()),
    )


def get_random_velocity(min_speed, max_speed):
    speed = random.uniform(min_speed, max_speed)
    angle = random.randrange(0, 360)
    return Vector2(speed, 0).rotate(angle)


def get_random_size(min_size, max_size):
    size = random.uniform(min_size, max_size)
    return size


def print_text(surface, text, font, rect_center, color=Color("red")):
    text_surface = font.render(text, True, color)

    rect = text_surface.get_rect()
    rect.center = rect_center

    surface.blit(text_surface, rect)


def draw_label(self, text, color):
    print_text(self.__screen, text, self.__font,
               self.__default_text_pos, color=color)


@staticmethod
def draw_buttons(lose_buttons):
    Mouse.updateMouseState()
    for button in lose_buttons:
        button.listen(event.get())
        button.draw()
