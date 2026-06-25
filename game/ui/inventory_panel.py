import pygame
from game.ui.slot import Slot

class InventoryPanel:
    def __init__(self, x, y, columns=5, rows=3, slot_size=60, spacing=5):
        self.x = x
        self.y = y
        self.slots = []
        self.font = pygame.font.SysFont(None, 16)
        self.selected_slot = None

        for row in range(rows):
            for col in range(columns):
                slot_x = x + col * (slot_size + spacing)
                slot_y = y + row * (slot_size + spacing)
                self.slots.append(Slot(slot_x, slot_y, slot_size))

    def update_from_inventory(self, inventory_slots):
        for i, slot in enumerate(self.slots):
            if i < len(inventory_slots) and inventory_slots[i]:
                stack = inventory_slots[i]
                slot.set_item(stack.item_id, stack.count, stack.durability)
            else:
                slot.clear()

    def handle_event(self, event):
        for slot in self.slots:
            if slot.handle_event(event):
                self.selected_slot = slot
                return slot
        return None

    def draw(self, screen):
        for slot in self.slots:
            slot.draw(screen, self.font)