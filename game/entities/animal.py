import pygame
import random
import math
from game.entities.enemy_base import Enemy

class Animal(Enemy):
    def __init__(self, x, y, animal_type):
        super().__init__(x, y, enemy_type=animal_type)
        self.wander_timer = 0
        self.wander_direction = (0, 0)
        self.flee_target = None

    def wander(self, structures=None):
        """Случайное блуждание"""
        if self.wander_timer <= 0:
            angle = random.uniform(0, 2 * math.pi)
            self.wander_direction = (math.cos(angle), math.sin(angle))
            self.wander_timer = random.randint(30, 90)

        dx = self.wander_direction[0] * self.speed * 0.5
        dy = self.wander_direction[1] * self.speed * 0.5

        new_x = self.x + dx
        new_y = self.y + dy

        # Проверка воды
        if self.environment and not self.environment.is_land(new_x, new_y):
            self.wander_timer = 0
            return

        # Проверка коллизий со стенами
        rect = pygame.Rect(new_x, new_y, self.size, self.size)
        collision = False
        if structures:
            for s in structures:
                if s.solid and rect.colliderect(s.get_rect()):
                    collision = True
                    break
        if not collision:
            self.x, self.y = new_x, new_y
        else:
            self.wander_timer = 0
        self.wander_timer -= 1

    def flee_from(self, target_x, target_y, structures=None):
        """Убегание от заданной точки"""
        dx = self.x - target_x
        dy = self.y - target_y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            speed = self.speed * 1.2
            new_x = self.x + dx * speed
            new_y = self.y + dy * speed

            # Проверка воды
            if self.environment and not self.environment.is_land(new_x, new_y):
                return  # стоим на месте, если путь в воду

            # Проверка коллизий со стенами
            rect = pygame.Rect(new_x, new_y, self.size, self.size)
            collision = False
            if structures:
                for s in structures:
                    if s.solid and rect.colliderect(s.get_rect()):
                        collision = True
                        break
            if not collision:
                self.x, self.y = new_x, new_y
            # иначе просто остаёмся на месте