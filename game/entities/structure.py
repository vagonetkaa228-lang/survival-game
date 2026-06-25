import pygame
from game.assets.sprites import blit_entity, blit_sprite

class Structure:
    def __init__(self, x, y, structure_type, width=40, height=40, solid=False):
        self.x = x # координата X верхнего левого угла
        self.y = y # координата Y верхнего левого угла
        self.type = structure_type # тип: tree, stone_vein, campfire, wall, door
        self.width = width # ширина хитбокса
        self.height = height # высота хитбокса
        self.solid = solid # блокирует ли движение
        self.health = 100 # текущее здоровье
        self.max_health = 100 # максимальное здоровье
        self.is_open = False if structure_type == "door" else None # для дверей: открыта ли (если не дверь – None)
        self.hit_timer = 0 # таймер подсветки при попадании

    def toggle(self):
        if self.type == "door": # если это дверь
            self.is_open = not self.is_open # переключаем состояние открытости
            self.solid = not self.is_open # если открыта – не твёрдая, и наоборот

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height) # прямоугольник для коллизий

    def update(self, player, enemies):
        pass # логика обновления не требуется

    def draw(self, surface, camera_x, camera_y, brightness=1.0):
        flash = min(1.0, self.hit_timer / 5.0) # интенсивность вспышки при попадании (0–1)

        if self.type == "campfire": # если костёр
            if brightness < 0.7: # если достаточно темно
                alpha = int((0.7 - brightness) * 300) # прозрачность свечения
                for radius_factor in [3, 5, 7]: # три кольца свечения разных размеров
                    glow_radius = self.width // 2 * radius_factor # радиус свечения
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA) # поверхность с альфа-каналом
                    pygame.draw.circle( # рисуем круг свечения
                        glow_surf, (255, 200, 100, alpha // radius_factor), # цвет и прозрачность
                        (glow_radius, glow_radius), glow_radius,
                    )
                    surface.blit( # отображаем свечение со смещением камеры
                        glow_surf,
                        (self.x - camera_x - glow_radius + self.width // 2,
                         self.y - camera_y - glow_radius + self.height // 2),
                    )
            blit_entity( # рисуем сам спрайт костра
                surface, "campfire", self.x, self.y, self.width,
                camera_x, camera_y,
                hit=self.hit_timer > 0, brightness=brightness,
            )
            return # выходим (дальше не рисуем)

        if self.type == "tree": # если дерево
            trunk = (101, 67, 33) # цвет ствола
            if flash: # если есть вспышка
                trunk = tuple(min(255, c + int(150 * flash)) for c in trunk) # осветляем ствол
            trunk_color = tuple(int(c * brightness) for c in trunk) # применяем яркость времени суток
            trunk_rect = pygame.Rect( # прямоугольник ствола
                self.x - camera_x + 5,
                self.y - camera_y + 10, 10, 20,
            )
            pygame.draw.rect(surface, trunk_color, trunk_rect) # рисуем ствол

            crown = (0, 100, 0) # цвет кроны
            if flash:
                crown = tuple(min(255, c + int(150 * flash)) for c in crown) # осветляем крону
            crown_color = tuple(int(c * brightness) for c in crown) # применяем яркость
            crown_center = (self.x - camera_x + 10, self.y - camera_y + 5) # центр кроны
            pygame.draw.circle(surface, crown_color, crown_center, 15) # рисуем крону (круг)
            return

        if self.type == "stone_vein": # если жила камня
            stone = (128, 128, 128) # серый цвет
            if flash:
                stone = tuple(min(255, c + int(150 * flash)) for c in stone) # осветляем
            color = tuple(int(c * brightness) for c in stone) # применяем яркость
            pygame.draw.rect( # рисуем камень как прямоугольник
                surface, color,
                (self.x - camera_x, self.y - camera_y, self.width, self.height),
            )
            return

        if self.type in ("wall", "door"): # если стена или дверь
            blit_sprite( # рисуем спрайт стены (общий для обоих)
                surface, "wall", self.x, self.y, (self.width, self.height),
                camera_x, camera_y,
                hit=self.hit_timer > 0, brightness=brightness,
            )
            if self.type == "door" and self.is_open: # если дверь открыта
                overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA) # полупрозрачная накладка
                overlay.fill((0, 180, 0, 90)) # зелёный полупрозрачный цвет
                surface.blit( # рисуем накладку поверх спрайта
                    overlay,
                    (int(self.x - camera_x), int(self.y - camera_y)),
                )
            return

        base = (101, 67, 33) # цвет по умолчанию (древесный) для неизвестных типов
        if flash:
            base = tuple(min(255, c + int(150 * flash)) for c in base) # осветляем
        color = tuple(int(c * brightness) for c in base) # применяем яркость
        pygame.draw.rect( # рисуем прямоугольник-заглушку
            surface, color,
            (self.x - camera_x, self.y - camera_y, self.width, self.height),
        )