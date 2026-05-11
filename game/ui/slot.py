import pygame
from game.items.registry import ITEMS

class Slot:
    def __init__(self, x, y, size=40):
        self.rect = pygame.Rect(x, y, size, size)
        self.item_id = None
        self.count = 0
        self.durability = None   # <-- новое поле
        self.selected = False
        self.hovered = False

    def set_item(self, item_id, count, durability=None):
        self.item_id = item_id
        self.count = count
        self.durability = durability

    def clear(self):
        self.item_id = None
        self.count = 0
        self.durability = None

    def draw(self, screen, font):
        # Рамка (цвет зависит от состояния)
        if self.selected:
            border_color = (255, 215, 0)
        elif self.hovered:
            border_color = (200, 200, 200)
        else:
            border_color = (100, 100, 100)

        pygame.draw.rect(screen, (50, 50, 50), self.rect)
        pygame.draw.rect(screen, border_color, self.rect, 4)

        if self.item_id and self.item_id in ITEMS:
            item = ITEMS[self.item_id]
            # Временная иконка – цветной квадрат
            if item.id in ["berry", "meat"]:
                color = (255, 100, 0)
            elif item.id in ["clean_water", "dirty_water"]:
                color = (0, 150, 255)
            else:
                color = (150, 150, 150)
            pygame.draw.rect(screen, color, self.rect.inflate(-6, -6))

            # Количество
            if self.count > 1:
                count_text = font.render(str(self.count), True, (255, 255, 255))
                screen.blit(count_text, (self.rect.right - 15, self.rect.bottom - 15))
            if self.durability is not None:
                dur_text = font.render(str(self.durability), True, (255, 255, 255))
                screen.blit(dur_text, (self.rect.left + 2, self.rect.top + 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                return True
        return False