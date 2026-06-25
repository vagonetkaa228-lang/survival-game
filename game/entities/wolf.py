
import math # для вычисления расстояний
import random # для случайных значений (скорость, здоровье)
from game.entities.enemy_base import Enemy # базовый класс врага

class Wolf(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="wolf") # вызываем конструктор Enemy с типом "wolf"
        self.speed = random.uniform(2, 2.5) # скорость 2-3 пикселя за кадр
        self.damage = 15 # урон за атаку
        self.health = random.uniform(100,150) # здоровье случайное от 100 до 150
        self.max_health = 120 # максимальное здоровье (среднее)
        self.sight_range = 250 # дальность обнаружения цели
        self.flee_health_threshold = 25 # при здоровье ниже 25 – убегать
        self.pack_call_range = 300 # радиус, в котором волки зовут стаю
        self.target = None # текущая цель (игрок или животное)

    def update_state(self, player, all_enemies=None, structures=None):
        if self.aggro_player: # если игрок агрессивен (ударил волка)
            self.state = "chase" # переходим в режим преследования
            self.target = player # цель – игрок
            return

        dist_to_player = math.hypot(player.x - self.x, player.y - self.y) # расстояние до игрока

        # поиск ближайшей добычи (травоядного) среди всех врагов
        nearest_prey = None
        min_prey_dist = float('inf')
        if all_enemies:
            for e in all_enemies:
                if (not hasattr(e, 'damage') or e.damage == 0) and e != self: # если существо без урона и не волк
                    d = math.hypot(self.x - e.x, self.y - e.y) # расстояние до добычи
                    if d < self.sight_range and d < min_prey_dist: # если в зоне видимости и ближе других
                        min_prey_dist = d
                        nearest_prey = e

        if nearest_prey: # если нашли добычу
            self.state = "chase" # преследуем её
            self.target = nearest_prey
        elif dist_to_player <= self.sight_range: # иначе если игрок рядом
            self.state = "chase" # преследуем игрока
            self.target = player
        else: # иначе
            self.state = "idle" # стоим
            self.target = None

        # стайный зов: если волк в режиме chase, то зовёт других волков в радиусе pack_call_range
        if self.state == "chase" and all_enemies:
            for other in all_enemies:
                if other is self or not isinstance(other, Wolf): # пропускаем себя и не-волков
                    continue
                if other.state != "chase": # если другой волк не в chase
                    d = math.hypot(self.x - other.x, self.y - other.y) # расстояние до него
                    if d <= self.pack_call_range: # если в радиусе зова
                        other.state = "chase" # переключаем его в chase
                        other.target = self.target # и даём ту же цель

    def act(self, player):
        if self.state == "chase" and self.target: # если в chase и есть цель
            self.move_towards(self.target.x, self.target.y, self.structures) # двигаемся к цели
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y) # дистанция до цели
            if dist <= self.attack_range and self.attack_cooldown <= 0: # если цель в радиусе атаки и кулдаун кончился
                self.target.health -= self.damage # наносим урон цели
                self.attack_cooldown = 30 # кулдаун 30 кадров


class StoryWolf(Wolf):
    """Волк для сюжетного эпизода: неактивен до триггера, может атаковать NPC."""
    def __init__(self, x, y):
        super().__init__(x, y) # вызываем конструктор Wolf
        self.episode_active = False # флаг активности эпизода (по умолчанию выключен)
        self.episode_survivor = None # ссылка на NPC, которого атакует (если есть)

    def update_state(self, player, all_enemies=None, structures=None):
        if not self.episode_active: # если эпизод не активен
            self.state = "idle" # стоим
            self.target = None
            return

        if self.aggro_player: # если игрок агрессивен (ударил волка)
            self.state = "chase" # преследуем игрока
            self.target = player
            return

        if self.episode_survivor: # если есть цель-выживший
            self.state = "chase" # преследуем его
            self.target = self.episode_survivor
            return

        self.state = "idle" # иначе стоим
        self.target = None

    def act(self, player):
        if self.state != "chase" or not self.target: # если не chase или нет цели
            return
        self.move_towards(self.target.x, self.target.y, self.structures) # двигаемся к цели
        dist = math.hypot(self.x - self.target.x, self.y - self.target.y) # дистанция
        if dist <= self.attack_range and self.attack_cooldown <= 0: # если близко и кулдаун готов
            if self.target is player: # если цель – игрок
                player.health -= self.damage # наносим урон игроку
            elif hasattr(self.target, "take_hit"): # если у цели есть метод take_hit (NPC)
                self.target.take_hit() # вызываем получение урона
            self.attack_cooldown = 30 # кулдаун


class WeakWolf(Wolf):
    """Слабый волк для обучения в прологе."""
    def __init__(self, x, y):
        super().__init__(x, y) # конструктор Wolf
        self.speed = random.uniform(1.5, 2.5) # меньшая скорость
        self.damage = 10 # меньший урон
        self.health = 40 # мало здоровья
        self.max_health = 40
        self.sight_range = 200 # меньшая дальность
        self.pack_call_range = 0 # не зовёт стаю
