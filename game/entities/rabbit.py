import pygame
import math
import random
from game.entities.animal import Animal

class Rabbit(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, "rabbit") # вызов конструктора Animal с типом "rabbit"
        self.size = 25 # маленький размер
        self.speed = random.uniform(4, 5) # очень быстрый (убегает)
        self.health = 20 # мало здоровья
        self.max_health = 20
        self.damage = 0 # не наносит урон
        self.sight_range = 180 # дальность обнаружения угроз
        self.state = "wander" # начальное состояние – блуждание

    def update_state(self, player, all_enemies=None, structures=None):
        threat = None # потенциальная угроза
        min_dist = float('inf') # минимальное расстояние до угрозы
        # Боится всех, кто может атаковать (damage > 0), включая игрока
        threats = [] # список угроз
        if all_enemies: # если есть враги
            for e in all_enemies: # перебираем
                if hasattr(e, 'damage') and e.damage > 0 and e != self: # если может атаковать и не сам заяц
                    threats.append(e) # добавляем в список
        threats.append(player) # игрок тоже угроза

        for t in threats: # перебираем все угрозы
            dist = math.hypot(self.x - t.x, self.y - t.y) # расстояние до угрозы
            if dist < self.sight_range and dist < min_dist: # если в зоне видимости и ближе других
                min_dist = dist
                threat = t # запоминаем ближайшую угрозу

        if threat: # если есть угроза
            self.state = "flee" # переходим в режим бегства
            self.flee_target = threat # цель для бегства
        else: # иначе
            self.state = "wander" # блуждаем

    def act(self, player):
        if self.state == "flee" and self.flee_target: # если режим бегства и есть цель
            self.flee_from(self.flee_target.x, self.flee_target.y, self.structures) # убегаем от цели
        else: # иначе
            self.wander(self.structures) # блуждаем