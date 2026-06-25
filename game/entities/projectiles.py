import pygame
import math

class Projectile:
    def __init__(self, x, y, angle, speed, damage, max_range=500):
        self.x = x # начальная X координата
        self.y = y # начальная Y координата
        self.vx = math.cos(angle) * speed # скорость по X (горизонтальная компонента)
        self.vy = math.sin(angle) * speed # скорость по Y (вертикальная компонента)
        self.damage = damage # урон снаряда
        self.distance_traveled = 0 # пройденное расстояние
        self.max_range = max_range # максимальная дальность полёта
        self.active = True # активен ли снаряд (жив)

    def update(self, enemies, structures, on_enemy_hit=None):
        if not self.active: # если не активен
            return # ничего не делаем
        self.x += self.vx # двигаем по X
        self.y += self.vy # двигаем по Y
        self.distance_traveled += abs(self.vx) + abs(self.vy) # накапливаем пройденный путь (приблизительно)

        # Проверка столкновения с твёрдыми структурами
        for s in structures: # перебираем все структуры
            if s.solid and s.get_rect().collidepoint(self.x, self.y): # если твёрдая и координаты внутри хитбокса
                self.active = False # деактивируем снаряд
                return
        # Проверка попадания во врагов
        for e in enemies: # перебираем всех врагов
            if e.get_rect().collidepoint(self.x, self.y): # если попадание в хитбокс врага
                e.health -= self.damage # наносим урон
                e.hit_timer = 5 # включаем подсветку попадания
                e.aggro_player = True # враг агрессивен к игроку
                if on_enemy_hit: # если передан коллбэк
                    on_enemy_hit(e) # вызываем его
                self.active = False # снаряд исчезает
                return
        if self.distance_traveled > self.max_range: # если пройдено больше максимальной дальности
            self.active = False # деактивируем

    def draw(self, surface, camera_x, camera_y):
        if self.active: # если активен
            pygame.draw.circle(surface, (255,255,0), # рисуем жёлтый круг
                               (int(self.x - camera_x), int(self.y - camera_y)), 3) # с учётом камеры, радиус 3