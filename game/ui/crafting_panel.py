import pygame
from game.items.registry import ITEMS
from game.crafting.recipes_list import get_recipes_for_player

class CraftingPanel:
    def __init__(self, x, y, width=300):
        self.x = x # X координата левого верхнего угла панели
        self.y = y # Y координата левого верхнего угла панели
        self.width = width # ширина панели
        self.height = 400 # высота панели (фиксированная)
        self.surface = pygame.Surface((self.width, self.height)) # поверхность для отрисовки (временная)
        self.buttons = []   # список кнопок (каждый элемент – словарь с rect, recipe, can)
        self.scroll_y = 0 # текущее смещение прокрутки (по вертикали)
        self.font = pygame.font.SysFont(None, 22) # основной шрифт для названия предмета
        self.sm_font = pygame.font.SysFont(None, 16) # маленький шрифт для ингредиентов

    def update_recipes(self, player, unlocked_story_ids=None):
        self.buttons.clear() # очищаем старые кнопки

        y = 0 # текущая вертикальная позиция для новой кнопки (без учёта скролла)
        for recipe in get_recipes_for_player(unlocked_story_ids): # получаем все доступные рецепты
            can = recipe.can_craft(player)  # проверяем, может ли игрок скрафтить сейчас
            btn_rect = pygame.Rect(5, y + 5, self.width - 10, 40) # прямоугольник кнопки
            self.buttons.append({'rect': btn_rect, 'recipe': recipe, 'can': can}) # добавляем кнопку
            y += 50 # шаг между кнопками
        self.max_scroll = max(0, y - self.height) # максимальное смещение прокрутки
        self.total_height = y  # общая высота всех кнопок (для создания поверхности)
        self.surface = pygame.Surface((self.width, self.total_height)) # создаём поверхность под весь список

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEWHEEL: # если событие колёсика мыши
            self.scroll_y -= event.y * 20 # смещаем прокрутку (event.y = ±1)
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll)) # ограничиваем
            return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # левый клик
            mx, my = event.pos # координаты мыши на экране
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height: # если клик внутри панели
                rel_y = my - self.y + self.scroll_y # относительная Y с учётом прокрутки
                for btn in self.buttons: # перебираем все кнопки
                    if btn['rect'].collidepoint(mx - self.x, rel_y): # если попадание
                        if btn['can']: # если можно скрафтить
                            result = btn['recipe'].craft(player) # выполняем крафт
                            if result: # если что-то получилось
                                return result # возвращаем id результата
        return None

    def draw(self, screen, player):
        self.surface.fill((40, 40, 40)) # заливаем фон поверхности (тёмно-серый)
        for btn in self.buttons: # рисуем каждую кнопку
            rect = btn['rect'] # прямоугольник кнопки (локальные координаты внутри self.surface)
            color = (60,80,60) if btn['can'] else (60,40,40) # зелёный, если доступно, иначе тёмно-красный
            pygame.draw.rect(self.surface, color, rect) # заливаем фон кнопки
            result_item = ITEMS[btn['recipe'].result_item_id] # получаем объект предмета-результата
            txt = self.font.render(result_item.name, True, (255,255,255)) # название предмета
            self.surface.blit(txt, (rect.x + 5, rect.y + 5)) # рисуем название
            # список ингредиентов с количеством
            ing_text = ", ".join([f"{ITEMS[ing].name}: {player.count_item(ing)}/{amt}"
                                  for ing, amt in btn['recipe'].ingredients.items()])
            ing_surf = self.sm_font.render(ing_text, True, (200,200,200)) # текст ингредиентов
            self.surface.blit(ing_surf, (rect.x + 5, rect.y + 22)) # рисуем ингредиенты чуть ниже
        screen.blit(self.surface, (self.x, self.y)) # рисуем панель на экране (без обрезки, но ниже будет обрезка)
        # заголовок над панелью
        title = self.font.render("КРАФТ", True, (220,180,100)) # золотистый заголовок
        view_rect = pygame.Rect(0, self.scroll_y, self.width, self.height) # область видимости (с учётом прокрутки)
        screen.blit(self.surface, (self.x, self.y), area=view_rect) # рисуем только видимую часть с прокруткой