import pygame
import math
import random
from game.entities.animal import Animal

class Fox(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, "fox")
        self.size = 35
        self.speed = random.uniform(2, 2.8)
        self.health = 60
        self.max_health = 60
        self.damage = 14
        self.attack_cooldown = 0
        self.sight_range = 300
        self.attack_range = 20
        self.state = "wander"
        self.target = None
        self.hostile_to_player = False

    def update_state(self, player, all_enemies=None, structures=None):
        if self.health <= 0:
            return

        if self.aggro_player:
            self.state = "chase"
            self.target = player
            return

        # Поиск ближайшего зайца
        nearest_rabbit = None
        min_dist = float('inf')
        if all_enemies:
            for e in all_enemies:
                if hasattr(e, 'type') and e.type == 'rabbit' and e != self:
                    dist = math.hypot(self.x - e.x, self.y - e.y)
                    if dist < self.sight_range and dist < min_dist:
                        min_dist = dist
                        nearest_rabbit = e

        if nearest_rabbit:
            self.state = "chase"
            self.target = nearest_rabbit
        else:
            self.state = "wander"
            self.target = None

    def act(self, player):
        if self.state == "chase" and self.target:
            self.move_towards(self.target.x, self.target.y, self.structures)
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y)
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                self.target.health -= self.damage
                self.attack_cooldown = 30
        else:
            self.wander(self.structures)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
