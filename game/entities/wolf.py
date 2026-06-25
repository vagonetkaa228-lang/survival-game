import math
import pygame
import random
from game.entities.enemy_base import Enemy

class Wolf(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="wolf")
        self.speed = random.uniform(2, 3)
        self.damage = 20
        self.health = random.uniform(100,150)
        self.max_health = 120
        self.sight_range = 250
        self.flee_health_threshold = 25
        self.pack_call_range = 300
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

        if self.state == "chase" and all_enemies:
            for other in all_enemies:
                if other is self or not isinstance(other, Wolf):
                    continue
                if other.state != "chase":
                    d = math.hypot(self.x - other.x, self.y - other.y)
                    if d <= self.pack_call_range:
                        other.state = "chase"
                        other.target = self.target

    def act(self, player):
        if self.state == "chase" and self.target:
            self.move_towards(self.target.x, self.target.y, self.structures)
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y)
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                self.target.health -= self.damage
                self.attack_cooldown = 30


class StoryWolf(Wolf):
    """Волк для сюжетного эпизода: неактивен до триггера, может атаковать NPC."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.episode_active = False
        self.episode_survivor = None

    def update_state(self, player, all_enemies=None, structures=None):
        if not self.episode_active:
            self.state = "idle"
            self.target = None
            return

        if self.aggro_player:
            self.state = "chase"
            self.target = player
            return

        if self.episode_survivor:
            self.state = "chase"
            self.target = self.episode_survivor
            return

        self.state = "idle"
        self.target = None

    def act(self, player):
        if self.state != "chase" or not self.target:
            return
        self.move_towards(self.target.x, self.target.y, self.structures)
        dist = math.hypot(self.x - self.target.x, self.y - self.target.y)
        if dist <= self.attack_range and self.attack_cooldown <= 0:
            if self.target is player:
                player.health -= self.damage
            elif hasattr(self.target, "take_hit"):
                self.target.take_hit()
            self.attack_cooldown = 30


class WeakWolf(Wolf):
    """Слабый волк для обучения в прологе."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = random.uniform(1.5, 2.5)
        self.damage = 10
        self.health = 40
        self.max_health = 40
        self.sight_range = 200
        self.pack_call_range = 0

