import pygame
import math

class Projectile:
    def __init__(self, x, y, angle, speed, damage, max_range=500):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.damage = damage
        self.distance_traveled = 0
        self.max_range = max_range
        self.active = True

    def update(self, enemies, structures):
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        self.distance_traveled += abs(self.vx) + abs(self.vy)

        # Проверка столкновения с твёрдыми структурами
        for s in structures:
            if s.solid and s.get_rect().collidepoint(self.x, self.y):
                self.active = False
                break
        # Проверка попадания во врагов
        for e in enemies:
            if e.get_rect().collidepoint(self.x, self.y):
                e.health -= self.damage
                e.hit_timer = 5
                e.aggro_player = True
                self.active = False
                break
        if self.distance_traveled > self.max_range:
            self.active = False

    def draw(self, surface, camera_x, camera_y):
        if self.active:
            pygame.draw.circle(surface, (255,255,0),
                               (int(self.x - camera_x), int(self.y - camera_y)), 3)