import pygame
import math
import random
from game.entities.animal import Animal

class Deer(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, "deer")
        self.size = 25
        self.speed = random.uniform(3, 5)   # достаточно быстрый
        self.health = 100
        self.max_health = 100
        self.damage = 0                          # безобидный
        self.sight_range = 290                   # далеко видит хищников
        self.state = "wander"                    # по умолчанию гуляет
        # flee_target будет назначен при появлении угрозы

    def update_state(self, player, all_enemies=None, structures=None):
        threat = None
        min_dist = float('inf')

        # Проверяем всех существ в мире
        if all_enemies:
            for e in all_enemies:
                # Угроза – любой, кто может атаковать (damage > 0) и не сам олень
                if hasattr(e, 'damage') and e.damage > 0 and e != self:
                    dist = math.hypot(self.x - e.x, self.y - e.y)
                    if dist < self.sight_range and dist < min_dist:
                        min_dist = dist
                        threat = e

        # Если игрок недавно ударил оленя, он тоже становится угрозой (даже без damage>0)
        if self.hit_timer > 0:
            dist = math.hypot(self.x - player.x, self.y - player.y)
            if dist < self.sight_range and dist < min_dist:
                min_dist = dist
                threat = player

        # Обновляем состояние
        if threat:
            self.state = "flee"
            self.flee_target = threat
        else:
            self.state = "wander"
            self.flee_target = None

    def act(self, player):
        if self.state == "flee" and self.flee_target:
            # Убегаем от источника опасности
            self.flee_from(self.flee_target.x, self.flee_target.y, self.structures)
        else:
            # Спокойно бродим
            self.wander(self.structures)

    def draw(self, surface, camera_x, camera_y):
        if self.dying:
            color = (128, 0, 0)
        elif self.hit_timer > 0:
            color = (255, 255, 255)
        else:
            color = (101, 67, 33)  # тёмно-коричневый
        pygame.draw.rect(surface, color,
                         (self.x - camera_x, self.y - camera_y, self.size, self.size))