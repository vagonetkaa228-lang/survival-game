import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, enemy_type="animal"):
        self.x = x
        self.y = y
        self.size = 20
        self.speed = random.uniform(2, 4.5)
        self.type = enemy_type
        self.health = 100
        self.max_health = 100
        self.damage = 5
        self.attack_cooldown = 0
        self.dying = False
        self.death_timer = 0
        self.hit_timer = 0
        self.aggro_player = False


        self.sight_range = 200
        self.attack_range = 30
        self.flee_health_threshold = 30
        self.state = "idle"
        self.target = None

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

    def update(self, player, all_enemies=None, structures = None, environment = None):
        self.structures = structures
        self.environment = environment
        if self.dying:
            self.death_timer -= 1
            if self.death_timer <= 0:
                return True
            return False

        if self.hit_timer > 0:
            self.hit_timer -= 1

        if self.health <= 0:
            self.dying = True
            self.death_timer = 100
            return False

        self.update_state(player, all_enemies)
        self.act(player)

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        return False

    def update_state(self, player, all_enemies=None, structures = None):
        dist = math.hypot(player.x - self.x, player.y - self.y)
        if self.health < self.flee_health_threshold:
            self.state = "flee"
        elif dist <= self.sight_range:
            self.state = "chase"
        else:
            self.state = "idle"

    def has_line_of_sight(self, player, structures):
            # Простая проверка: если нет стен между self и player
            x1, y1 = self.x + self.size // 2, self.y + self.size // 2
            x2, y2 = player.x + player.size // 2, player.y + player.size // 2
            for s in structures:
                if s.solid and s.get_rect().clipline((x1, y1), (x2, y2)):
                    return False
            return True

    def act(self, player):
        if self.state == "chase":
            self.move_towards(player.x, player.y, self.structures)
            dist = math.hypot(player.x - self.x, player.y - self.y)
            if dist <= self.attack_range and self.attack_cooldown <= 0:
                player.health -= self.damage
                self.attack_cooldown = 30
        elif self.state == "flee":
            self.move_away(player.x, player.y, self.structures)

    def move_towards(self, target_x, target_y, structures):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed

            new_x = self.x + dx
            new_y = self.y + dy

            # Проверка воды (если окружение задано)
            if self.environment and not self.environment.is_land(new_x, new_y):
                return  # не заходим в воду

            # Проверка коллизий по X
            rect = pygame.Rect(new_x, self.y, self.size, self.size)
            for s in structures or []:
                if s.solid and rect.colliderect(s.get_rect()):
                    if dx > 0:
                        new_x = s.x - self.size
                    elif dx < 0:
                        new_x = s.x + s.width
                    break
            # Повторная проверка воды после корректировки по X
            if self.environment and not self.environment.is_land(new_x, self.y):
                return
            self.x = new_x

            # Проверка коллизий по Y
            new_y = self.y + dy
            rect = pygame.Rect(self.x, new_y, self.size, self.size)
            for s in structures or []:
                if s.solid and rect.colliderect(s.get_rect()):
                    if dy > 0:
                        new_y = s.y - self.size
                    elif dy < 0:
                        new_y = s.y + s.height
                    break
            # Повторная проверка воды после корректировки по Y
            if self.environment and not self.environment.is_land(self.x, new_y):
                return
            self.y = new_y

    def move_away(self, target_x, target_y, structures):
        dx = self.x - target_x
        dy = self.y - target_y
        dist = math.hypot(dx, dy)
        if dist > 1:
            dx = dx / dist * self.speed
            dy = dy / dist * self.speed

            new_x = self.x + dx
            new_y = self.y + dy

            # Проверка воды
            if self.environment and not self.environment.is_land(new_x, new_y):
                return

            # Проверка коллизий по X
            rect = pygame.Rect(new_x, self.y, self.size, self.size)
            for s in structures or []:
                if s.solid and rect.colliderect(s.get_rect()):
                    if dx > 0:
                        new_x = s.x - self.size
                    elif dx < 0:
                        new_x = s.x + s.width
                    break
            if self.environment and not self.environment.is_land(new_x, self.y):
                return
            self.x = new_x

            # Проверка коллизий по Y
            new_y = self.y + dy
            rect = pygame.Rect(self.x, new_y, self.size, self.size)
            for s in structures or []:
                if s.solid and rect.colliderect(s.get_rect()):
                    if dy > 0:
                        new_y = s.y - self.size
                    elif dy < 0:
                        new_y = s.y + s.height
                    break
            if self.environment and not self.environment.is_land(self.x, new_y):
                return
            self.y = new_y
    def draw(self, surface, camera_x, camera_y):
        if self.dying:
            color = (128, 0, 0)
            pygame.draw.rect(surface, color,
                             (self.x - camera_x, self.y - camera_y, self.size, self.size))
        else:
            color = (255, 255, 255) if self.hit_timer > 0 else (255, 0, 0)
            pygame.draw.rect(surface, color,
                             (self.x - camera_x, self.y - camera_y, self.size, self.size))