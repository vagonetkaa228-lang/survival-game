import pygame
import random
from game.items.registry import ITEMS

class Loot:
    def __init__(self, x, y, item_id=None):
        self.x = x
        self.y = y
        self.size = 10
        if item_id is None:
            # Для совместимости оставим случайную еду/воду
            self.item_id = random.choice(["berry", "clean_water"])
        else:
            self.item_id = item_id
        self.item = ITEMS.get(self.item_id)

    def draw(self, surface, camera_x, camera_y):
        if self.item:
            # Цвет можно задавать по типу предмета
            if "food" in self.item_id or self.item_id == "berry":
                color = (255, 200, 0)
            elif "water" in self.item_id:
                color = (0, 200, 255)
            else:
                color = (200, 200, 200)
        else:
            color = (255, 0, 255)  # ошибка
        pygame.draw.rect(surface, color,
                         (self.x - camera_x, self.y - camera_y, self.size, self.size))