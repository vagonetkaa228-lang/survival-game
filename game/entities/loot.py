import pygame
import random
from game.items.registry import ITEMS

class Loot:
    def __init__(self, x, y, item_id=None):
        self.x = x
        self.y = y
        self.size = 25 if item_id == "stone" else 20
        if item_id is None:
            # Для совместимости оставим случайную еду/воду
            self.item_id = random.choice(["berry", "clean_water"])
        else:
            self.item_id = item_id
        self.item = ITEMS.get(self.item_id)

    def draw(self, surface, camera_x, camera_y):
        from game.assets.sprites import blit_sprite, get_item_sprite_name
        name = get_item_sprite_name(self.item_id)
        blit_sprite(
            surface, name, self.x, self.y, self.size,
            camera_x, camera_y,
        )