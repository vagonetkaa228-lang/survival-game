
import math
import random
from game.entities.animal import Animal

class Fox(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, "fox") # вызов конструктора Animal с типом "fox"
        self.size = 35 # размер хитбокса (меньше, чем у волка)
        self.speed = random.uniform(2, 2.8) # скорость 2–2.8 пикселя/кадр
        self.health = 60 # здоровье лисы
        self.max_health = 60
        self.damage = 14 # урон за атаку
        self.attack_cooldown = 0 # таймер перезарядки атаки
        self.sight_range = 300 # дальность обнаружения добычи
        self.attack_range = 20 # радиус атаки (ближе, чем у волка)
        self.state = "wander" # начальное состояние – блуждание
        self.target = None # текущая цель (заяц или игрок)
        self.hostile_to_player = False # не агрессивна к игроку по умолчанию

    def update_state(self, player, all_enemies=None, structures=None):
        if self.health <= 0: # если мертва
            return

        if self.aggro_player: # если игрок ударил лису
            self.state = "chase" # преследовать игрока
            self.target = player
            return

        # Поиск ближайшего зайца
        nearest_rabbit = None # ближайший заяц
        min_dist = float('inf') # минимальное расстояние
        if all_enemies: # если передан список всех врагов
            for e in all_enemies: # перебираем всех
                if hasattr(e, 'type') and e.type == 'rabbit' and e != self: # если это заяц и не сама лиса
                    dist = math.hypot(self.x - e.x, self.y - e.y) # расстояние до зайца
                    if dist < self.sight_range and dist < min_dist: # если в пределах видимости и ближе других
                        min_dist = dist
                        nearest_rabbit = e

        if nearest_rabbit: # если нашли зайца
            self.state = "chase" # преследовать
            self.target = nearest_rabbit
        else: # иначе
            self.state = "wander" # блуждать
            self.target = None

    def act(self, player):
        if self.state == "chase" and self.target: # если состояние chase и есть цель
            self.move_towards(self.target.x, self.target.y, self.structures) # двигаемся к цели
            dist = math.hypot(self.x - self.target.x, self.y - self.target.y) # расстояние до цели
            if dist <= self.attack_range and self.attack_cooldown <= 0: # если цель в радиусе атаки и кулдаун готов
                self.target.health -= self.damage # наносим урон цели
                self.attack_cooldown = 30 # ставим кулдаун
        else: # иначе (не chase или нет цели)
            self.wander(self.structures) # блуждаем

        if self.attack_cooldown > 0: # если кулдаун активен
            self.attack_cooldown -= 1 # уменьшаем его