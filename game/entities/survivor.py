import pygame
import math

class Survivor:
    def __init__(self, x, y, survivor_type='survivor', name=None):
        self.x = x # координата X
        self.y = y # координата Y
        self.size = 40 # размер хитбокса
        self.found = False # найден ли игроком
        self.type = survivor_type # тип выжившего (для спрайта)
        self.name = name or survivor_type # имя (или тип)
        self.story_npc = False # флаг сюжетного NPC
        self.dialogue_completed = False # диалог завершён
        self.hit_timer = 0 # таймер подсветки попадания
        self.in_water = False # находится ли в воде
        self.water_bob = 0.0 # фаза покачивания на воде

    def take_hit(self):
        self.hit_timer = 18 # включаем подсветку (18 кадров)

    def update(self):
        if self.in_water: # если в воде
            self.water_bob += 0.08 # увеличиваем фазу покачивания
        if self.hit_timer > 0: # если таймер подсветки активен
            self.hit_timer -= 1 # уменьшаем его

    def draw(self, surface, camera_x, camera_y):
        bob = int(math.sin(self.water_bob) * 4) if self.in_water else 0 # смещение вверх-вниз на воде
        from game.assets.sprites import blit_entity # импорт внутри метода
        blit_entity( # рисуем выжившего
            surface, self.type, self.x, self.y + bob, self.size, # поверхность, тип, позиция, размер
            camera_x, camera_y, # смещение камеры
            hit=self.hit_timer > 0, # подсветка при попадании
        )