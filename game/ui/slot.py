import pygame
from game.items.registry import ITEMS

class Slot:
    def __init__(self, x, y, size=40):
        self.rect = pygame.Rect(x, y, size, size) # прямоугольник слота
        self.item_id = None # id предмета (или None)
        self.count = 0 # количество предметов в стаке
        self.durability = None # прочность (для инструментов/оружия)
        self.selected = False # выбран ли слот (рамка золотая)
        self.hovered = False # наведена ли мышь

    def set_item(self, item_id, count, durability=None):
        self.item_id = item_id # устанавливаем id предмета
        self.count = count # устанавливаем количество
        self.durability = durability # устанавливаем прочность (если есть)

    def clear(self):
        self.item_id = None # очищаем id
        self.count = 0 # обнуляем количество
        self.durability = None # очищаем прочность

    def draw(self, screen, font):
        # Рамка (цвет зависит от состояния)
        if self.selected: # если выбран
            border_color = (255, 215, 0) # золотой
        elif self.hovered: # если наведён
            border_color = (200, 200, 200) # светло-серый
        else: # иначе
            border_color = (100, 100, 100) # тёмно-серый

        pygame.draw.rect(screen, (50, 50, 50), self.rect) # фон слота (тёмный)
        pygame.draw.rect(screen, border_color, self.rect, 4) # рамка с нужным цветом

        if self.item_id and self.item_id in ITEMS: # если есть предмет в реестре
            from game.assets.sprites import blit_item
            blit_item(screen, self.item_id, self.rect) # рисуем иконку предмета в слоте

            # Количество
            if self.count > 1: # если больше одного
                count_text = font.render(str(self.count), True, (255, 255, 255)) # текст количества
                screen.blit(count_text, (self.rect.right - 15, self.rect.bottom - 15)) # в правом нижнем углу
            if self.durability is not None: # если есть прочность
                dur_text = font.render(str(self.durability), True, (255, 255, 255)) # текст прочности
                screen.blit(dur_text, (self.rect.left + 2, self.rect.top + 2)) # в левом верхнем углу

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: # если движение мыши
            self.hovered = self.rect.collidepoint(event.pos) # обновляем hovered
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # если левый клик
            if self.hovered: # если наведены
                return True # возвращаем True (слот активирован)
        return False # иначе ничего