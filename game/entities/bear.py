import pygame
import math
import random
from game.entities.enemy_base import Enemy

class Bear(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="bear")
        self.size = 35
        self.speed = random.uniform(0.8, 1.5)
        self.damage = 20
        self.health = 250
        self.max_health = 250
        self.sight_range = 300
        self.attack_range = 40
        self.flee_health_threshold = 0   # медведь не убегает
        self.target = None

    def update_state(self, player, all_enemies=None, structures=None):
        if self.aggro_player:
            self.state = "chase"
            self.target = player
            return

        dist_to_player = math.hypot(player.x - self.x, player.y - self.y)

        nearest_prey = None
        min_prey_dist = float('inf')
        if all_enemies:
            for e in all_enemies:
                if (not hasattr(e, 'damage') or e.damage == 0) and e != self:
                    d = math.hypot(self.x - e.x, self.y - e.y)
                    if d < self.sight_range and d < min_prey_dist:
                        min_prey_dist = d
                        nearest_prey = e

        if nearest_prey:
            self.state = "chase"
            self.target = nearest_prey
        elif dist_to_player <= self.sight_range:
            self.state = "chase"
            self.target = player
        else:
            self.state = "idle"
            self.target = None

    def act(self, player):
        if self.state == "chase" and self.target:
            self.move_towards(self.target.x, self.target.y, self.structures)
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y)
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                self.target.health -= self.damage
                self.attack_cooldown = 30
        # idle – ничего не делаем

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def draw(self, surface, camera_x, camera_y):
        if self.dying:
            color = (128, 0, 0)
        elif self.hit_timer > 0:
            color = (255, 255, 255)
        else:
            color = (152, 118, 84)   # тёмно-коричневый
        pygame.draw.rect(surface, color,
                         (self.x - camera_x, self.y - camera_y, self.size, self.size))