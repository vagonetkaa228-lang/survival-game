
import random
from game.items.registry import ITEMS

class Loot:
    def __init__(self, x, y, item_id=None):
        self.x = x # координата X
        self.y = y # координата Y
        self.size = 25 if item_id == "stone" else 20 # размер лута: камень крупнее
        if item_id is None: # если id не передан (для совместимости)
            self.item_id = random.choice(["berry", "clean_water"]) # случайный предмет
        else:
            self.item_id = item_id # сохраняем переданный id
        self.item = ITEMS.get(self.item_id) # объект предмета из реестра

    def draw(self, surface, camera_x, camera_y):
        from game.assets.sprites import blit_sprite, get_item_sprite_name # импорт внутри метода
        name = get_item_sprite_name(self.item_id) # имя спрайта для предмета
        blit_sprite( # отрисовка лута
            surface, name, self.x, self.y, self.size, # поверхность, имя, позиция, размер
            camera_x, camera_y, # смещение камеры
        )