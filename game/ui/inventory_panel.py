import pygame
from game.ui.slot import Slot

class InventoryPanel:
    def __init__(self, x, y, columns=5, rows=3, slot_size=60, spacing=5):
        self.x = x # X координата левого верхнего угла панели
        self.y = y # Y координата левого верхнего угла панели
        self.slots = [] # список всех слотов инвентаря
        self.font = pygame.font.SysFont(None, 16) # маленький шрифт для количества
        self.selected_slot = None # выбранный слот (для операций)

        for row in range(rows): # перебираем строки
            for col in range(columns): # перебираем столбцы
                slot_x = x + col * (slot_size + spacing) # X слота
                slot_y = y + row * (slot_size + spacing) # Y слота
                self.slots.append(Slot(slot_x, slot_y, slot_size)) # создаём слот и добавляем в список

    def update_from_inventory(self, inventory_slots):
        for i, slot in enumerate(self.slots): # перебираем все слоты панели
            if i < len(inventory_slots) and inventory_slots[i]: # если есть предмет в инвентаре
                stack = inventory_slots[i] # получаем стак предмета
                slot.set_item(stack.item_id, stack.count, stack.durability) # устанавливаем данные в слот
            else:
                slot.clear() # иначе очищаем слот

    def handle_event(self, event):
        for slot in self.slots: # перебираем слоты
            if slot.handle_event(event): # если слот обработал событие (клик/наведение)
                self.selected_slot = slot # запоминаем выбранный слот
                return slot # возвращаем его
        return None

    def draw(self, screen):
        for slot in self.slots: # перебираем все слоты
            slot.draw(screen, self.font) # рисуем каждый слот