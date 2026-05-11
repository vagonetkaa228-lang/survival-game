import pygame

class HUD:
    def __init__(self, font_size=24):
        self.font = pygame.font.SysFont(None, font_size)
        self.displayed_hp = 100.0
        self.icon_food = pygame.Surface((20, 20))
        self.icon_food.fill((255, 200, 0))
        self.icon_water = pygame.Surface((20, 20))
        self.icon_water.fill((0, 200, 255))

    def update(self, player_health):
        self.displayed_hp += (player_health - self.displayed_hp) * 0.1

    def draw(self, screen, player):
        pygame.draw.rect(screen, (0, 0, 0), (10, 10, 260, 90))
        pygame.draw.rect(screen, (255, 255, 255), (10, 10, 260, 90), 2)

        hp_ratio = max(0, self.displayed_hp) / 100
        pygame.draw.rect(screen, (255, 0, 0), (20, 20, 200, 10))
        pygame.draw.rect(screen, (0, 255, 0), (20, 20, 200 * hp_ratio, 10))

        # Энергия
        energy_ratio = max(0, player.energy) / player.max_energy
        pygame.draw.rect(screen, (0, 0, 250), (20, 30, 200 * energy_ratio, 8))
        pygame.draw.rect(screen, (255, 255, 255), (20, 30, 200, 8), 1)

        screen.blit(self.icon_food, (20, 40))
        screen.blit(self.icon_water, (20, 65))

        food_text = self.font.render(f"Сытость: {int(player.hunger)}", True, (255, 255, 255))
        water_text = self.font.render(f"Утоленость: {int(player.thirst)}", True, (255, 255, 255))
        screen.blit(food_text, (50, 40))
        screen.blit(water_text, (50, 65))

        slot_size = 44
        start_x = (screen.get_width() // 2) - (len(player.hotbar) * (slot_size + 4)) // 2
        y = screen.get_height() - slot_size - 10
        for i in range(len(player.hotbar)):
            rect = pygame.Rect(start_x + i * (slot_size + 4), y, slot_size, slot_size)
            pygame.draw.rect(screen, (60, 60, 60), rect)

            # рамка выбранного слота
            if player.get_hotbar_item(i) == player.active_item_id:
                pygame.draw.rect(screen, (255, 215, 0), rect, 5)
            else:
                pygame.draw.rect(screen, (150, 150, 150), rect, 1)

            item_id = player.hotbar[i]
            if item_id:
                stack = player.inventory.get(item_id)  # получаем один раз

                # Иконка
                from game.items.registry import ITEMS
                item = ITEMS.get(item_id)
                if item:
                    if hasattr(item, 'tool_type'):
                        color = (245, 184, 0)
                    else:
                        color = (150, 150, 100)
                    icon_rect = rect.inflate(-10, -10)
                    pygame.draw.rect(screen, color, icon_rect)

                # Прочность (если есть)
                if stack and stack.durability is not None:
                    dur_text = self.font.render(str(stack.durability), True, (255, 255, 255))
                    # Размещаем в левом верхнем углу иконки
                    screen.blit(dur_text, (rect.x + 4, rect.y + 4))