
import math
import random
from game.entities.enemy_base import Enemy

class Bear(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, enemy_type="bear") # вызываем конструктор Enemy с типом "bear"
        self.size = 50 # увеличиваем размер до 50 (
        self.speed = random.uniform(1.5, 2) # скорость
        self.damage = 20 # высокий урон
        self.health = random.uniform(400, 500) # много здоровья
        self.max_health = 500 # максимальное здоровье
        self.sight_range = 300 # дальность обнаружения больше
        self.attack_range = 40 # чуть больше дистанция атаки
        self.flee_health_threshold = 0 # медведь никогда не убегает
        self.target = None # цель пока не выбрана

    def update_state(self, player, all_enemies=None, structures=None):
        if self.aggro_player: # если игрок вызвал агрессию (например, ударил)
            self.state = "chase" # переключаемся в режим преследования
            self.target = player # цель – игрок
            return

        dist_to_player = math.hypot(player.x - self.x, player.y - self.y) # расстояние до игрока

        nearest_prey = None # ближайшая добыча (животное)
        min_prey_dist = float('inf') # минимальное расстояние до добычи
        if all_enemies: # если список врагов передан
            for e in all_enemies: # перебираем всех врагов
                if (not hasattr(e, 'damage') or e.damage == 0) and e != self: # если существо без урона (травоядное) и это не сам медведь
                    d = math.hypot(self.x - e.x, self.y - e.y) # расстояние до добычи
                    if d < self.sight_range and d < min_prey_dist: # если в радиусе видимости и ближе других
                        min_prey_dist = d # обновляем минимальное расстояние
                        nearest_prey = e # запоминаем добычу

        if nearest_prey: # если нашли добычу
            self.state = "chase" # преследуем её
            self.target = nearest_prey # цель – добыча
        elif dist_to_player <= self.sight_range: # иначе если игрок рядом
            self.state = "chase" # преследуем игрока
            self.target = player
        else:
            self.state = "idle" # иначе стоим
            self.target = None

    def act(self, player):
        if self.state == "chase" and self.target: # если в режиме преследования и есть цель
            self.move_towards(self.target.x, self.target.y, self.structures) # двигаемся к цели
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y) # дистанция до цели
            if dist <= self.attack_range and self.attack_cooldown <= 0: # если цель в радиусе атаки и кулдаун кончился
                self.target.health -= self.damage # наносим урон цели
                self.attack_cooldown = 30 # ставим кулдаун (30 кадров)
        # idle – ничего не делаем

        if self.attack_cooldown > 0: # если кулдаун активен
            self.attack_cooldown -= 1 # уменьшаем его

class StoryBear(Bear):
    """Медведь для сюжетного эпизода — неактивен до атаки игрока."""
    def __init__(self, x, y):
        super().__init__(x, y) # вызываем конструктор Bear
        self.episode_active = False # флаг активности эпизода (изначально выключен)

    def update(self, player, all_enemies=None, structures=None, environment=None):
        self.structures = structures # сохраняем структуры
        self.environment = environment # сохраняем окружение
        if self.dying: # если медведь умирает
            self.death_timer -= 1 # уменьшаем таймер смерти
            return self.death_timer <= 0 # возвращаем True, когда таймер станет <= 0 (удалить)
        if self.hit_timer > 0: # если есть подсветка попадания
            self.hit_timer -= 1 # уменьшаем её
        if self.health <= 0: # если здоровье кончилось
            self.dying = True # включаем анимацию смерти
            self.death_timer = 100 # задержка 100 кадров
            return False # пока не удаляем
        if not self.episode_active: # если эпизод не активен
            return False # не двигаемся и не атакуем
        self.update_state(player, all_enemies, structures) # обновляем состояние (если эпизод активен)
        self.act(player) # выполняем действие
        return False # не удаляем

    def update_state(self, player, all_enemies=None, structures=None):
        if not self.episode_active: # если эпизод не активен
            self.state = "idle" # стоим на месте
            self.target = None # нет цели
            return
        if self.aggro_player: # если игрок агрессивен (ударил медведя)
            self.state = "chase" # преследуем игрока
            self.target = player # цель – игрок
            return
        dist = math.hypot(player.x - self.x, player.y - self.y) # расстояние до игрока
        if dist <= self.sight_range: # если игрок в пределах видимости
            self.state = "chase" # преследуем
            self.target = player
        else:
            self.state = "idle" # иначе стоим
            self.target = None