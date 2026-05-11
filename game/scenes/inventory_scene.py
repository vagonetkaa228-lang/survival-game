import pygame
import random
from game.entities.loot import Loot
from game.ui.inventory_panel import InventoryPanel
from game.ui.crafting_panel import CraftingPanel
from game.ui.button import Button
from game.items.registry import ITEMS

class InventoryScene:
    def __init__(self, player, game_scene):
        self.player = player
        self.game_scene = game_scene
        self.font = pygame.font.SysFont(None, 24)

        self.inv_panel = InventoryPanel(50, 100, columns=5, rows=4)
        self.craft_panel = CraftingPanel(400, 100, width=350)
        self.close_btn = Button("Закрыть (I)", 50, 500, 150, 40)

        self.update_panels()

    def update_panels(self):
        self.inv_panel.update_from_inventory(self.player.inventory)
        self.craft_panel.update_recipes(self.player)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            return self.game_scene

        if self.close_btn.clicked(event):
            return self.game_scene

        # Клик по слоту инвентаря
        slot = self.inv_panel.handle_event(event)
        if slot and slot.item_id:
            self.player.use_item(slot.item_id)
            self.update_panels()
            return self

        # Клик по кнопке крафта
        result = self.craft_panel.handle_event(event, self.player)
        if result:
            from game.items.registry import ITEMS
            from game.items.tool import Tool
            item = ITEMS.get(result)
            if item and isinstance(item, Tool):
                self.player.add_to_hotbar(result)
            self.update_panels()
            return self

        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            if self.inv_panel.selected_slot and self.inv_panel.selected_slot.item_id:
                item_id = self.inv_panel.selected_slot.item_id
                if self.player.remove_item(item_id, 1):
                    loot_x = self.player.x + random.randint(-20, 20)
                    loot_y = self.player.y + random.randint(-20, 20)
                    self.game_scene.loots.append(Loot(loot_x, loot_y, item_id))
                    self.update_panels()
            return self
        return self


    def update(self):
        self.close_btn.update()
        for btn in self.craft_panel.buttons:
            btn.update()

    def draw(self, screen):

            # Фон в стиле Rust – тёмно-коричневый
            screen.fill((30, 25, 20))

            # Рамка вокруг всего интерфейса
            pygame.draw.rect(screen, (100, 70, 40), (20, 20, 760, 560), 4)
            pygame.draw.rect(screen, (60, 40, 30), (24, 24, 752, 552), 2)

            # Заголовок с "металлическим" шрифтом
            title = self.font.render("ИНВЕНТАРЬ", True, (220, 180, 100))
            screen.blit(title, (100, 50))

            self.inv_panel.draw(screen)
            self.craft_panel.draw(screen, self.player)
            self.close_btn.draw(screen, self.font)

            # Подсказка
            hint = self.font.render("ЛКМ – использовать / скрафтить", True, (180, 160, 120))
            screen.blit(hint, (300, 500))

            # Тултип при наведении на слот
            mouse_pos = pygame.mouse.get_pos()
            for slot in self.inv_panel.slots:
                if slot.hovered and slot.item_id:
                    item = ITEMS[slot.item_id]
                    lines = [
                        item.name,
                        item.description,
                        f"Количество: {slot.count}"
                    ]
                    # Вычисляем размеры фона
                    font = self.font
                    max_width = max([font.size(line)[0] for line in lines]) + 20
                    line_height = 22
                    height = len(lines) * line_height + 10

                    # Позиция (справа-снизу от курсора)
                    tooltip_x = mouse_pos[0] + 15
                    tooltip_y = mouse_pos[1] + 15

                    # Фон
                    pygame.draw.rect(screen, (40, 40, 40), (tooltip_x - 5, tooltip_y - 5, max_width, height))
                    pygame.draw.rect(screen, (150, 150, 150), (tooltip_x - 5, tooltip_y - 5, max_width, height), 2)

                    # Текст
                    for i, line in enumerate(lines):
                        text_surf = font.render(line, True, (255, 255, 255))
                        screen.blit(text_surf, (tooltip_x, tooltip_y + i * line_height))
                    break  # показываем только один тултип (первый найденный слот)
        #screen.fill((20, 20, 30))
        #
        # title = self.font.render("ИНВЕНТАРЬ", True, (255, 255, 255))
        # screen.blit(title, (50, 30))
        #
        # self.inv_panel.draw(screen)
        # self.craft_panel.draw(screen, self.player)
        # self.close_btn.draw(screen, self.font)
        #
        # # Тултип при наведении на слот
        # mouse_pos = pygame.mouse.get_pos()
        # for slot in self.inv_panel.slots:
        #     if slot.hovered and slot.item_id:
        #         item = ITEMS[slot.item_id]
        #         lines = [
        #             item.name,
        #             item.description,
        #             f"Количество: {slot.count}"
        #         ]
        #         # Вычисляем размеры фона
        #         font = self.font
        #         max_width = max([font.size(line)[0] for line in lines]) + 20
        #         line_height = 22
        #         height = len(lines) * line_height + 10
        #
        #         # Позиция (справа-снизу от курсора)
        #         tooltip_x = mouse_pos[0] + 15
        #         tooltip_y = mouse_pos[1] + 15
        #
        #         # Фон
        #         pygame.draw.rect(screen, (40, 40, 40), (tooltip_x - 5, tooltip_y - 5, max_width, height))
        #         pygame.draw.rect(screen, (150, 150, 150), (tooltip_x - 5, tooltip_y - 5, max_width, height), 2)
        #
        #         # Текст
        #         for i, line in enumerate(lines):
        #             text_surf = font.render(line, True, (255, 255, 255))
        #             screen.blit(text_surf, (tooltip_x, tooltip_y + i * line_height))
        #         break  # показываем только один тултип (первый найденный слот)
        #
        # # Подсказка
        # hint = self.font.render("Клик по предмету – использовать", True, (180, 180, 180))
        # screen.blit(hint, (50, 560))