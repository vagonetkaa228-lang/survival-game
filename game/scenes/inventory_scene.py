import pygame # для работы с графикой и событиями
import random # для случайного разброса лута
from game.entities.loot import Loot # класс лута (предмет на земле)
from game.ui.inventory_panel import InventoryPanel # панель инвентаря
from game.ui.crafting_panel import CraftingPanel # панель крафта
from game.ui.button import Button # кнопка
from game.items.registry import ITEMS # реестр всех предметов

class InventoryScene:
    def __init__(self, player, game_scene):
        self.player = player # ссылка на игрока
        self.game_scene = game_scene # ссылка на игровую сцену (для доступа к луту и сюжету)
        self.font = pygame.font.SysFont(None, 24) # шрифт для текста

        self.inv_panel = InventoryPanel(50, 100, columns=5, rows=4) # панель инвентаря (5x4)
        self.craft_panel = CraftingPanel(400, 100, width=350) # панель крафта
        self.close_btn = Button("Закрыть (I)", 50, 500, 150, 40) # кнопка закрытия

        self.update_panels() # обновляем содержимое панелей

    def update_panels(self):
        self.inv_panel.update_from_inventory(self.player.inventory_slots) # обновляем инвентарь из игрока
        unlocked = getattr(self.game_scene, "unlocked_story_recipes", []) # получаем открытые сюжетные рецепты
        self.craft_panel.update_recipes(self.player, unlocked) # обновляем крафт с учётом рецептов

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_i: # если нажата I
            return self.game_scene # закрываем инвентарь (возврат в игру)

        if self.close_btn.clicked(event): # если нажата кнопка закрыть
            return self.game_scene

        # Клик по слоту инвентаря
        slot = self.inv_panel.handle_event(event) # проверяем клик по слотам
        if slot and slot.item_id: # если кликнули по слоту с предметом
            self.player.use_item(slot.item_id) # используем предмет (еда, вода, инструмент)
            self.update_panels() # обновляем панели (количество могло измениться)
            return self # остаёмся в инвентаре

        # Клик по кнопке крафта
        result = self.craft_panel.handle_event(event, self.player) # крафтим предмет
        if result: # если что-то скрафтилось
            if result == "raft": # если скрафтили плот – переход к концовке побега
                from game.story.escape_ending import EscapeEndingScene
                gs = self.game_scene
                pilot = gs.pilot_rescue.pilot if gs.pilot_rescue else None
                captain = gs.captain_rescue.captain if gs.captain_rescue else None
                return EscapeEndingScene(self.player, pilot, captain)
            from game.items.registry import ITEMS
            from game.items.tool import Tool
            item = ITEMS.get(result)
            if item and isinstance(item, Tool): # если скрафтили инструмент
                self.player.add_to_hotbar(result) # автоматически добавляем в хотбар
            self.update_panels() # обновляем панели
            return self

        if event.type == pygame.KEYDOWN and event.key == pygame.K_q: # если нажата Q (выбросить)
            if self.inv_panel.selected_slot and self.inv_panel.selected_slot.item_id: # если выбран слот
                item_id = self.inv_panel.selected_slot.item_id # id предмета
                if self.player.remove_item(item_id, 1): # удаляем один предмет
                    loot_x = self.player.x + random.randint(-20, 20) # координаты для лута (рядом с игроком)
                    loot_y = self.player.y + random.randint(-20, 20)
                    self.game_scene.loots.append(Loot(loot_x, loot_y, item_id)) # создаём лут на земле
                    self.update_panels() # обновляем панели
            return self

        return self # ничего не делаем

    def update(self):
        self.close_btn.update() # обновляем кнопку (hover и т.д.)
        self.update_panels() # обновляем панели (на случай, если инвентарь изменился вне событий)
        for btn in self.craft_panel.buttons: # обновляем все кнопки крафта
            btn.update()

    def draw(self, screen):
        # Фон
        screen.fill((30, 25, 20)) # тёмно-коричневый фон

        # Рамка вокруг всего интерфейса
        pygame.draw.rect(screen, (100, 70, 40), (20, 20, 760, 560), 4) # внешняя рамка
        pygame.draw.rect(screen, (60, 40, 30), (24, 24, 752, 552), 2) # внутренняя рамка

        # Заголовок с "металлическим" шрифтом
        title = self.font.render("ИНВЕНТАРЬ", True, (220, 180, 100)) # золотистый цвет
        screen.blit(title, (100, 50))

        self.inv_panel.draw(screen) # рисуем панель инвентаря
        self.craft_panel.draw(screen, self.player) # рисуем панель крафта
        self.close_btn.draw(screen, self.font) # рисуем кнопку закрытия

        # Тултип при наведении на слот
        mouse_pos = pygame.mouse.get_pos() # позиция мыши
        for slot in self.inv_panel.slots: # перебираем слоты
            if slot.hovered and slot.item_id: # если наведены и есть предмет
                item = ITEMS[slot.item_id] # получаем объект предмета
                lines = [ # строки для тултипа
                    item.name, # название
                    item.description, # описание
                    f"Количество: {slot.count}" # количество
                ]
                # Вычисляем размеры фона
                font = self.font
                max_width = max([font.size(line)[0] for line in lines]) + 20 # ширина с отступами
                line_height = 22
                height = len(lines) * line_height + 10 # высота с отступами

                # Позиция (справа-снизу от курсора)
                tooltip_x = mouse_pos[0] + 15
                tooltip_y = mouse_pos[1] + 15

                # Фон
                pygame.draw.rect(screen, (40, 40, 40), (tooltip_x - 5, tooltip_y - 5, max_width, height)) # тёмный фон
                pygame.draw.rect(screen, (150, 150, 150), (tooltip_x - 5, tooltip_y - 5, max_width, height), 2) # рамка

                # Текст
                for i, line in enumerate(lines):
                    text_surf = font.render(line, True, (255, 255, 255)) # белый текст
                    screen.blit(text_surf, (tooltip_x, tooltip_y + i * line_height))
                break # показываем только один тултип (первый найденный слот)