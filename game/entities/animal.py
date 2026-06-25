import pygame
import random
import math
from game.entities.enemy_base import Enemy

class Animal(Enemy):
    def __init__(self, x, y, animal_type):
        super().__init__(x, y, enemy_type=animal_type) # вызов конструктора родительского класса
        self.wander_timer = 0 # таймер до смены направления блуждания
        self.wander_direction = (0, 0) # текущее направление блуждания (вектор)
        self.flee_target = None # точка, от которой убегаем (если есть)

    def wander(self, structures=None):
        """Случайное блуждание"""
        if self.wander_timer <= 0: # если таймер истёк
            angle = random.uniform(0, 2 * math.pi) # случайный угол
            self.wander_direction = (math.cos(angle), math.sin(angle)) # вычисляем направление по углу
            self.wander_timer = random.randint(30, 90) # новый таймер (кадры)
        dx = self.wander_direction[0] * self.speed * 0.5 # смещение по X (половинная скорость)
        dy = self.wander_direction[1] * self.speed * 0.5 # смещение по Y
        new_x = self.x + dx # пробуем новую позицию X
        new_y = self.y + dy # пробуем новую позицию Y
        if self.environment and not self.environment.is_land(new_x, new_y): # если вода
            self.wander_timer = 0 # сбрасываем таймер, чтобы сменить направление
            return # не двигаемся
        rect = pygame.Rect(new_x, new_y, self.size, self.size) # хитбокс для проверки столкновений
        collision = False # флаг столкновения
        if structures: # если есть структуры
            for s in structures: # перебираем все структуры
                if s.solid and rect.colliderect(s.get_rect()): # если твёрдая и пересекается
                    collision = True # была коллизия
                    break
        if not collision: # если нет коллизий
            self.x, self.y = new_x, new_y # применяем новую позицию
        else: # иначе
            self.wander_timer = 0 # сбрасываем таймер (чтобы сразу сменить направление)
        self.wander_timer -= 1 # уменьшаем таймер каждый кадр

    def flee_from(self, target_x, target_y, structures=None):
        """Убегание от заданной точки"""
        dx = self.x - target_x # вектор от цели к животному (по X)
        dy = self.y - target_y # вектор от цели к животному (по Y)
        dist = math.hypot(dx, dy) # расстояние до цели
        if dist > 0: # если расстояние больше нуля
            dx /= dist # нормализуем вектор
            dy /= dist
            speed = self.speed * 1.2 # скорость убегания (чуть быстрее обычной)
            new_x = self.x + dx * speed # новая позиция X
            new_y = self.y + dy * speed # новая позиция Y
            if self.environment and not self.environment.is_land(new_x, new_y): # если вода
                return # стоим на месте, не двигаемся
            rect = pygame.Rect(new_x, new_y, self.size, self.size) # хитбокс
            collision = False # флаг коллизии
            if structures: # если есть структуры
                for s in structures: # перебор
                    if s.solid and rect.colliderect(s.get_rect()): # столкновение
                        collision = True
                        break
            if not collision: # если нет столкновений
                self.x, self.y = new_x, new_y # применяем новую позицию
            # иначе просто остаёмся на месте