import pygame
import math
import random
from game.entities.animal import Animal

class Rabbit(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, "rabbit")
        self.size = 12
        self.speed = random.uniform(4, 5)
        self.health = 20
        self.max_health = 20
        self.damage = 0
        self.sight_range = 180
        self.state = "wander"

    def update_state(self, player, all_enemies=None, structures=None):
        threat = None
        min_dist = float('inf')
        # Боится всех, кто может атаковать (damage > 0), включая игрока
        threats = []
        if all_enemies:
            for e in all_enemies:
                if hasattr(e, 'damage') and e.damage > 0 and e != self:
                    threats.append(e)
        threats.append(player)

        for t in threats:
            dist = math.hypot(self.x - t.x, self.y - t.y)
            if dist < self.sight_range and dist < min_dist:
                min_dist = dist
                threat = t

        if threat:
            self.state = "flee"
            self.flee_target = threat
        else:
            self.state = "wander"

    def act(self, player):
        if self.state == "flee" and self.flee_target:
            self.flee_from(self.flee_target.x, self.flee_target.y, self.structures)
        else:
            self.wander(self.structures)

    def draw(self, surface, camera_x, camera_y):
        if self.dying:
            color = (128, 0, 0)
        elif self.hit_timer > 0:
            color = (255, 200, 200)  # светло-розовый (для контраста)
        else:
            color = (255, 255, 255)  # белый
        pygame.draw.rect(surface, color,
                         (self.x - camera_x, self.y - camera_y, self.size, self.size))