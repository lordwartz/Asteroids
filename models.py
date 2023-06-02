from pygame.math import Vector2
from pygame.transform import rotozoom
from utils import get_random_velocity, load_sprite, wrap_position


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() // 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        blit_position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, blit_position)

    def move(self, surface):
        self.position = wrap_position(self.position + self.velocity, surface)

    def collides_with(self, other_obj):
        if self and other_obj:
            distance = self.position.distance_to(other_obj.position)
            return distance < self.radius + other_obj.radius
        else:
            raise Exception("Unable to check collision for non-existing object")


class Spaceship(GameObject):
    MANEUVERABILITY = 3
    ACCELERATION = 0.25
    BULLET_SPEED = 3
    SPACESHIP_ANTIGRAVITY = 0.05

    def __init__(self, position, create_bullet_callback):
        self.score = 0
        self.lives = 3
        self.create_bullet_callback = create_bullet_callback
        self.is_alive = True

        self.direction = Vector2(0, -1)
        super().__init__(position, load_sprite("spaceship"), Vector2(0))

    def add_score(self, score_value):
        self.score += score_value

    def rotate(self, clockwise=True):
        sign = 1 if clockwise else -1
        angle = self.MANEUVERABILITY * sign
        self.direction.rotate_ip(angle)

    def draw(self, surface):
        angle = self.direction.angle_to(Vector2(0, -1))
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())
        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def accelerate(self):
        self.velocity += self.direction * self.ACCELERATION

    def not_accelerate(self):
        if self.velocity != Vector2(0, 0):
            self.velocity -= self.velocity * self.SPACESHIP_ANTIGRAVITY

    def shoot(self):
        bullet_velocity = self.direction * self.BULLET_SPEED + self.velocity
        bullet = Bullet(self.position, bullet_velocity, True)
        self.create_bullet_callback(bullet)


class Asteroid(GameObject):
    def __init__(self, position, create_asteroid_callback,
                 initial_size, reduction_size=3):
        self.create_asteroid_callback = create_asteroid_callback
        self.reduction_size = reduction_size
        self.initial_size = initial_size

        size_to_scale = {
            3: 1,
            2: 0.5,
            1: 0.25,
        }

        scale = size_to_scale[reduction_size]
        sprite = rotozoom(load_sprite("asteroid"), 0, self.initial_size *
                          scale)

        super().__init__(
            position, sprite, get_random_velocity(0.25, 1)
        )

    def split(self, spaceship):
        size_to_score = {
            3: 25,
            2: 50,
            1: 100,
        }

        spaceship.score += size_to_score[self.reduction_size]
        if self.reduction_size > 1:
            for _ in range(2):
                asteroid = Asteroid(
                    self.position, self.create_asteroid_callback,
                    self.initial_size, self.reduction_size - 1
                )
                self.create_asteroid_callback(asteroid)


class Bullet(GameObject):
    def __init__(self, position, velocity, is_spaceship_bullet):
        if is_spaceship_bullet:
            super().__init__(position, load_sprite("bullet"), velocity)
        else:
            super().__init__(position, load_sprite("enemy_bullet"), velocity)

    def move(self, surface):
        self.position = self.position + self.velocity


class Ufo(GameObject):
    BULLET_SPEED = 1
    BULLET_FREQUENCY = 25

    def __init__(self, position, velocity, create_bullet_callback):
        self.create_bullet_callback = create_bullet_callback
        self.current_frame = 0
        self.velocity = velocity

        sprite = rotozoom(load_sprite("ufo"), 0, 1)
        super().__init__(position, sprite, self.velocity)

    def move(self, surface):
        self.position = self.position + self.velocity
        self.current_frame += 1

    def shoot(self):
        bullet_velocity = get_random_velocity(1, 2) * self.BULLET_SPEED \
                          + self.velocity
        bullet = Bullet(self.position, bullet_velocity, False)
        self.create_bullet_callback(bullet)
