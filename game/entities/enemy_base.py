import pygame
import math
import random

class Enemy:
    def __init__(self, x, y, enemy_type="animal"):
        self.x = x # координата X верхнего левого угла
        self.y = y # координата Y верхнего левого угла
        self.size = 40 # размер стороны  квадрат
        self.speed = random.uniform(2, 3) # скорость движения (пикселей/кадр)
        self.type = enemy_type # строка для выбора спрайта
        self.health = 100 # текущее здоровье
        self.max_health = 100 # максимальное здоровье
        self.damage = 5 # урон за одну атаку
        self.attack_cooldown = 0 # таймер до следующей атаки (кадры)
        self.dying = False # флаг начала анимации смерти
        self.death_timer = 0 # счётчик до удаления из списка
        self.hit_timer = 0 # таймер белой вспышки при попадании
        self.aggro_player = False # (задел) состояние агрессии
        self.sight_range = 200 # дистанция обнаружения игрока
        self.attack_range = 30 # радиус для удара (от края до края)
        self.flee_health_threshold = 30 # при здоровье ниже – бежать
        self.state = "idle" # текущее состояние: idle/chase/flee
        self.target = None # цель (обычно игрок)
        self.structures = None # список структур
        self.environment = None # объект мира

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size) # прямоугольник для коллизий

    def update(self, player, all_enemies=None, structures=None, environment=None):
        self.structures = structures # сохраняем структуры для движения
        self.environment = environment # сохраняем окружение для проверки воды
        if self.dying: # если уже мёртв
            self.death_timer -= 1 # уменьшаем таймер удаления
            if self.death_timer <= 0: # если время вышло
                return True # удалить объект из списка
            return False # ещё не удалять
        if self.hit_timer > 0: # если есть подсветка попадания
            self.hit_timer -= 1 # уменьшаем таймер подсветки
        if self.health <= 0: # если здоровье опустилось до нуля
            self.dying = True # начинаем анимацию смерти
            self.death_timer = 100 # задержка перед удалением (100 кадров)
            return False # пока не удаляем
        self.update_state(player, all_enemies) # пересчитываем состояние ИИ
        self.act(player) # выполняем действие (движение/атаку)
        if self.attack_cooldown > 0: # если перезарядка атаки идёт
            self.attack_cooldown -= 1 # уменьшаем на 1 кадр
        return False # объект жив, не удаляем

    def update_state(self, player, all_enemies=None, structures=None):
        dist = math.hypot(player.x - self.x, player.y - self.y) # расстояние до игрока
        if self.health < self.flee_health_threshold: # если здоровье ниже порога страха
            self.state = "flee" # переключаемся в режим бегства
        elif dist <= self.sight_range: # если игрок в поле зрения
            self.state = "chase" # переключаемся в режим преследования
        else: # иначе
            self.state = "idle" # стоим на месте

    def has_line_of_sight(self, player, structures):
        x1, y1 = self.x + self.size // 2, self.y + self.size // 2 # центр врага
        x2, y2 = player.x + player.size // 2, player.y + player.size // 2 # центр игрока
        for s in structures: # перебираем все структуры
            if s.solid and s.get_rect().clipline((x1, y1), (x2, y2)): # если стена перекрывает линию
                return False # видимости нет
        return True # видимость есть

    def act(self, player):
        if self.state == "chase": # если режим преследования
            self.move_towards(player.x, player.y, self.structures) # двигаемся к игроку
            dist = math.hypot(player.x - self.x, player.y - self.y) # текущая дистанция
            if dist <= self.attack_range and self.attack_cooldown <= 0: # если близко и атака готова
                player.health -= self.damage # наносим урон игроку
                self.attack_cooldown = 30 # ставим кулдаун (30 кадров)
        elif self.state == "flee": # если режим бегства
            self.move_away(player.x, player.y, self.structures) # двигаемся от игрока

    def move_towards(self, target_x, target_y, structures):
        dx = target_x - self.x # разница по X до цели
        dy = target_y - self.y # разница по Y до цели
        dist = math.hypot(dx, dy) # расстояние до цели
        if dist > 1: # если расстояние больше 1 пикселя
            dx = dx / dist * self.speed # нормализованное направление * скорость
            dy = dy / dist * self.speed # нормализованное направление * скорость
            new_x = self.x + dx # пробуем новую позицию по X
            new_y = self.y + dy # пробуем новую позицию по Y
            if self.environment and not self.environment.is_land(new_x, new_y): # если вода
                return # не двигаемся
            rect = pygame.Rect(new_x, self.y, self.size, self.size) # хитбокс на новом X (Y старый)
            for s in structures or []: # проверяем все структуры
                if s.solid and rect.colliderect(s.get_rect()): # если столкновение
                    if dx > 0: # если двигались вправо
                        new_x = s.x - self.size # прижать к левой границе стены
                    elif dx < 0: # если двигались влево
                        new_x = s.x + s.width # прижать к правой границе стены
                    break # выходим из цикла
            if self.environment and not self.environment.is_land(new_x, self.y): # проверка воды после коррекции
                return # не двигаемся
            self.x = new_x # применяем новую X
            new_y = self.y + dy # пробуем новую позицию по Y (X уже обновлён)
            rect = pygame.Rect(self.x, new_y, self.size, self.size) # хитбокс на новом Y
            for s in structures or []: # проверяем все структуры
                if s.solid and rect.colliderect(s.get_rect()): # если столкновение
                    if dy > 0: # если двигались вниз
                        new_y = s.y - self.size # прижать к верхней границе стены
                    elif dy < 0: # если двигались вверх
                        new_y = s.y + s.height # прижать к нижней границе стены
                    break # выходим из цикла
            if self.environment and not self.environment.is_land(self.x, new_y): # проверка воды после коррекции
                return # не двигаемся
            self.y = new_y # применяем новую Y

    def move_away(self, target_x, target_y, structures):
        dx = self.x - target_x # вектор от игрока к врагу (по X)
        dy = self.y - target_y # вектор от игрока к врагу (по Y)
        dist = math.hypot(dx, dy) # расстояние до игрока
        if dist > 1: # если расстояние больше 1 пикселя
            dx = dx / dist * self.speed # нормализованное направление * скорость
            dy = dy / dist * self.speed # нормализованное направление * скорость
            new_x = self.x + dx # пробуем новую позицию по X
            new_y = self.y + dy # пробуем новую позицию по Y
            if self.environment and not self.environment.is_land(new_x, new_y): # если вода
                return # не двигаемся
            rect = pygame.Rect(new_x, self.y, self.size, self.size) # хитбокс на новом X
            for s in structures or []: # проверяем все структуры
                if s.solid and rect.colliderect(s.get_rect()): # если столкновение
                    if dx > 0: # если двигались вправо
                        new_x = s.x - self.size # прижать к левой границе стены
                    elif dx < 0: # если двигались влево
                        new_x = s.x + s.width # прижать к правой границе стены
                    break # выходим из цикла
            if self.environment and not self.environment.is_land(new_x, self.y): # проверка воды после коррекции
                return # не двигаемся
            self.x = new_x # применяем новую X
            new_y = self.y + dy # пробуем новую позицию по Y
            rect = pygame.Rect(self.x, new_y, self.size, self.size) # хитбокс на новом Y
            for s in structures or []: # проверяем все структуры
                if s.solid and rect.colliderect(s.get_rect()): # если столкновение
                    if dy > 0: # если двигались вниз
                        new_y = s.y - self.size # прижать к верхней границе стены
                    elif dy < 0: # если двигались вверх
                        new_y = s.y + s.height # прижать к нижней границе стены
                    break # выходим из цикла
            if self.environment and not self.environment.is_land(self.x, new_y): # проверка воды после коррекции
                return # не двигаемся
            self.y = new_y # применяем новую Y

    def draw(self, surface, camera_x, camera_y):
        from game.assets.sprites import blit_entity # импортируем функцию отрисовки
        blit_entity( # вызываем отрисовку с параметрами
            surface, self.type, self.x, self.y, self.size, # поверхность, тип, позиция, размер
            camera_x, camera_y, # смещение камеры
            hit=self.hit_timer > 0, # подсветка при попадании
            dying=self.dying, # анимация смерти
        )