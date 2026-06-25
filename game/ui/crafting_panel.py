import pygame
from game.ui.button import Button
from game.items.registry import ITEMS
from game.crafting.recipes_list import get_recipes_for_player

class CraftingPanel:
    def __init__(self, x, y, width=300):
        self.x = x
        self.y = y
        self.width = width
        self.height = 400
        self.surface = pygame.Surface((self.width, self.height))
        self.buttons = []   # это будут словари с rect и recipe
        self.scroll_y = 0
        self.font = pygame.font.SysFont(None, 22)
        self.sm_font = pygame.font.SysFont(None, 16)

    def update_recipes(self, player, unlocked_story_ids=None):
        self.buttons.clear()

        y = 0
        for recipe in get_recipes_for_player(unlocked_story_ids):
            can = recipe.can_craft(player)  # ← передаём игрока
            btn_rect = pygame.Rect(5, y + 5, self.width - 10, 40)
            self.buttons.append({'rect': btn_rect, 'recipe': recipe, 'can': can})
            y += 50
        self.max_scroll = max(0, y - self.height)
        self.total_height = y  # общая высота всех кнопок
        self.surface = pygame.Surface((self.width, self.total_height))


    def handle_event(self, event, player):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_y -= event.y * 20
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                rel_y = my - self.y + self.scroll_y
                for btn in self.buttons:
                    if btn['rect'].collidepoint(mx - self.x, rel_y):
                        if btn['can']:
                            result = btn['recipe'].craft(player)
                            if result:
                                return result
        return None

    def draw(self, screen, player):
        self.surface.fill((40, 40, 40))
        for btn in self.buttons:
            rect = btn['rect']
            color = (60,80,60) if btn['can'] else (60,40,40)
            pygame.draw.rect(self.surface, color, rect)
            # ингредиенты...
            # надпись
            result_item = ITEMS[btn['recipe'].result_item_id]
            txt = self.font.render(result_item.name, True, (255,255,255))
            self.surface.blit(txt, (rect.x + 5, rect.y + 5))
            # список ингредиентов
            ing_text = ", ".join([f"{ITEMS[ing].name}: {player.count_item(ing)}/{amt}"
                                  for ing, amt in btn['recipe'].ingredients.items()])
            ing_surf = self.sm_font.render(ing_text, True, (200,200,200))
            self.surface.blit(ing_surf, (rect.x + 5, rect.y + 22))
        screen.blit(self.surface, (self.x, self.y))
        # заголовок над панелью
        title = self.font.render("КРАФТ", True, (220,180,100))
        view_rect = pygame.Rect(0, self.scroll_y, self.width, self.height)
        screen.blit(self.surface, (self.x, self.y), area=view_rect)