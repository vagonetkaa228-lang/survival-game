import pygame
from game.settings import WIDTH, HEIGHT, BLUE, WORLD_WIDTH, WORLD_HEIGHT
from game.items.tool import Tool
from game.items.item_stack import ItemStack
import math

INVENTORY_SIZE = 20  # максимальное количество слотов в инвентаре

class Player:
    def __init__(self):
        # Позиция в мире (изначально по центру, потом переопределяется)
        self.x = WIDTH // 2 # начальная X (заменится позже)
        self.y = HEIGHT // 2 # начальная Y
        self.speed = 2 # базовая скорость (устаревшее)
        self.size = 40 # размер хитбокса игрока
        # Основные характеристики
        self.hunger = 100 # голод (0-100)
        self.thirst = 100 # жажда (0-100)
        self.health = 100 # здоровье (0-100)
        # Позиция в мире (по центру карты)
        self.x = WORLD_WIDTH // 2 # реальная X
        self.y = WORLD_HEIGHT // 2 # реальная Y
        # Боевые параметры
        self.attack_cooldown = 0 # задержка между атаками (кадры)
        self.attack_range = 50 # дальность атаки в пикселях
        self.attack_damage = 25 # урон от атаки
        self.attack_timer = 0 # таймер анимации удара
        self.attack_angle = 0 # направление удара (в радианах)
        self.alive = True # жив ли игрок
        # Инвентарь и хотбар
        self.inventory_slots = [None] * INVENTORY_SIZE # 20 слотов инвентаря
        self.selected_item = None # устаревшее
        self.hotbar = [None] * 5 # 5 слотов быстрого доступа
        self.active_item_id = None # ID активного предмета из хотбара
        # Энергия для бега
        self.energy = 100 # текущая энергия
        self.max_energy = 100 # максимальная энергия
        self.walk_speed = 1 # скорость ходьбы
        self.run_speed = 2 # скорость бега

    def _find_empty_slot(self):
        """Находит первый свободный слот в инвентаре"""
        for i, slot in enumerate(self.inventory_slots): # проходим по слотам
            if slot is None: # если слот пуст
                return i # возвращаем индекс
        return None # свободных слотов нет

    def _get_stack_in_slot(self, item_id):
        """Находит стопку с указанным предметом в инвентаре"""
        for stack in self.inventory_slots: # перебираем все слоты
            if stack and stack.item_id == item_id: # если стопка с таким id
                return stack # возвращаем её
        return None

    def has_item(self, item_id):
        """Проверяет, есть ли у игрока хотя бы один предмет"""
        return self.count_item(item_id) > 0 # количество > 0

    def clean_hotbar(self):
        """Удаляет из хотбара предметы, которых больше нет в инвентаре"""
        for i in range(len(self.hotbar)): # для каждого слота хотбара
            item_id = self.hotbar[i]
            if item_id is not None and not self.has_item(item_id): # если предмет пропал
                self.hotbar[i] = None # очищаем слот
        if self.active_item_id is not None and not self.has_item(self.active_item_id): # если активный предмет пропал
            self.active_item_id = None # убираем его

    def count_item(self, item_id):
        """Считает общее количество предметов данного ID в инвентаре"""
        return sum( # суммируем
            stack.count for stack in self.inventory_slots # количество в каждой стопке
            if stack and stack.item_id == item_id # только если предмет совпадает
        )

    def set_hotbar_slot(self, index, item_id):
        """Устанавливает предмет в слот хотбара по индексу"""
        if 0 <= index < len(self.hotbar): # если индекс допустим
            self.hotbar[index] = item_id # устанавливаем

    def get_hotbar_item(self, index):
        """Возвращает ID предмета из слота хотбара"""
        if 0 <= index < len(self.hotbar): # если индекс допустим
            return self.hotbar[index] # возвращаем
        return None

    def use_hotbar_item(self, index):
        """Использует предмет из хотбара (для еды/воды)"""
        item_id = self.get_hotbar_item(index) # получаем id
        self.active_item_id = item_id # делаем активным
        if item_id is None: # если пусто
            return
        from game.items.registry import ITEMS # импорт внутри метода
        item = ITEMS.get(item_id)
        if item: # если предмет существует
            if hasattr(item, 'hunger_restore') or hasattr(item, 'thirst_restore'): # если еда или вода
                self.use_item(item_id) # используем

    def add_item(self, item_id, amount=1, durability=None):
        """
        Добавляет предмет в инвентарь.
        Возвращает True если все предметы поместились, False если не хватило места
        """
        from game.items.registry import ITEMS
        prototype = ITEMS.get(item_id) # получаем прототип предмета
        if not prototype: # если предмета нет в реестре
            return False
        remaining = amount # сколько осталось добавить
        added_any = False # был ли добавлен хоть один
        max_stack = prototype.max_stack # максимальный размер стопки
        if max_stack == 1: # нестакающиеся предметы (оружие, инструменты)
            while remaining > 0:
                slot_idx = self._find_empty_slot() # ищем пустой слот
                if slot_idx is None: # нет свободных
                    break
                self.inventory_slots[slot_idx] = ItemStack(item_id, 1, durability) # создаём стопку
                remaining -= 1
                added_any = True
        else: # стакающиеся предметы
            # сначала добавляем в существующие стопки
            for stack in self.inventory_slots:
                if stack and stack.item_id == item_id and stack.count < max_stack:
                    can_add = min(remaining, max_stack - stack.count) # сколько можем добавить
                    stack.count += can_add
                    remaining -= can_add
                    added_any = True
                    if remaining <= 0:
                        break
            # остаток кладём в новые слоты
            while remaining > 0:
                slot_idx = self._find_empty_slot()
                if slot_idx is None:
                    break
                chunk = min(remaining, max_stack)
                self.inventory_slots[slot_idx] = ItemStack(item_id, chunk, durability)
                remaining -= chunk
                added_any = True
        if added_any and hasattr(prototype, 'tool_type'): # если добавили инструмент
            self.add_to_hotbar(item_id) # добавляем в хотбар
        return added_any and remaining == 0 # все ли добавлены

    def remove_item(self, item_id, amount=1):
        """Удаляет указанное количество предметов из инвентаря"""
        if self.count_item(item_id) < amount: # если недостаточно
            return False
        remaining = amount
        for i, stack in enumerate(self.inventory_slots):
            if not stack or stack.item_id != item_id:
                continue
            take = min(remaining, stack.count) # сколько взять из этой стопки
            stack.count -= take
            remaining -= take
            if stack.count <= 0: # если стопка опустела
                self.inventory_slots[i] = None # удаляем слот
            if remaining <= 0:
                break
        self.clean_hotbar() # обновляем хотбар
        return True

    def obtain_pistol(self):
        """Выдаёт игроку пистолет (особый метод для сюжета)"""
        if self.has_item("pistol"): # если пистолет уже есть
            self.add_item("magazine", 8) # даём обойму
        else:
            self.add_item("pistol", 1, durability=8) # даём пистолет с 8 патронами
            self.add_to_hotbar("pistol") # добавляем в хотбар

    def use_item(self, item_id):
        """Использует предмет (еда/вода)"""
        from game.items.registry import ITEMS
        if not self.has_item(item_id) or item_id not in ITEMS:
            return False
        item = ITEMS[item_id]
        if hasattr(item, 'hunger_restore') or hasattr(item, 'thirst_restore'):
            if item.use(self): # применяем эффект
                return self.remove_item(item_id, 1) # удаляем один предмет
        return False

    def add_to_hotbar(self, item_id):
        """Добавляет предмет в хотбар, если его там ещё нет"""
        if item_id is None:
            return
        for i in range(len(self.hotbar)):
            if self.hotbar[i] == item_id: # если уже есть
                self.active_item_id = item_id # делаем активным
                return
        for i in range(len(self.hotbar)):
            if self.hotbar[i] is None: # находим свободный слот
                self.hotbar[i] = item_id
                self.active_item_id = item_id
                return
        self.hotbar[0] = item_id # если все заняты – заменяем первый
        self.active_item_id = item_id

    def attack(self, enemies, mouse_pos=None, damage=None):
        """Атакует врагов в радиусе attack_range"""
        if self.attack_cooldown > 0 or not self.alive: # если на кулдауне или мёртв
            return
        hit_damage = damage if damage is not None else self.attack_damage
        if mouse_pos: # определяем направление удара
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            self.attack_angle = math.atan2(dy, dx)
        else:
            self.attack_angle = 0
        self.attack_timer = 10 # запускаем анимацию
        for e in enemies: # проходим по врагам
            dx = e.x - self.x
            dy = e.y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.attack_range: # если в радиусе
                e.health -= hit_damage
                e.hit_timer = 5 # анимация попадания
                e.aggro_player = True # враг агрится
        self.attack_cooldown = 30 # задержка 0.5 сек

    def move(self, keys, structures):
        """Двигает игрока с учётом коллизий со структурами"""
        if not self.alive:
            return
        if keys[pygame.K_LSHIFT] and self.energy > 0: # бег
            current_speed = self.run_speed
            self.energy = max(0, self.energy - 0.3) # расход энергии
        else:
            current_speed = self.walk_speed
            self.energy = min(100, self.energy + 0.1) # восстановление
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= current_speed
        if keys[pygame.K_s]: dy += current_speed
        if keys[pygame.K_a]: dx -= current_speed
        if keys[pygame.K_d]: dx += current_speed
        # коллизии по X
        new_x = self.x + dx
        player_rect = pygame.Rect(new_x, self.y, self.size, self.size)
        for s in structures:
            if s.solid and player_rect.colliderect(s.get_rect()):
                if dx > 0:
                    new_x = s.x - self.size
                elif dx < 0:
                    new_x = s.x + s.width
                break
        # коллизии по Y
        new_y = self.y + dy
        player_rect = pygame.Rect(self.x, new_y, self.size, self.size)
        for s in structures:
            if s.solid and player_rect.colliderect(s.get_rect()):
                if dy > 0:
                    new_y = s.y - self.size
                elif dy < 0:
                    new_y = s.y + s.height
                break
        self.x, self.y = new_x, new_y

    def interact(self, structures):
        """Взаимодействие с ближайшей дверью (переключение открыта/закрыта)"""
        if not self.alive:
            return
        interaction_range = 50
        for s in structures:
            if s.type == "door": # только двери
                door_center_x = s.x + s.width // 2
                door_center_y = s.y + s.height // 2
                dist = math.hypot(
                    self.x + self.size // 2 - door_center_x,
                    self.y + self.size // 2 - door_center_y
                )
                if dist <= interaction_range:
                    s.toggle() # переключаем
                    break

    def update(self):
        """Обновляет состояние игрока каждый кадр (голод, жажда, здоровье)"""
        if not self.alive:
            return
        self.hunger -= 0.008 # трата голода
        self.thirst -= 0.009 # трата жажды
        if self.hunger <= 0 or self.thirst <= 0:
            self.health -= 0.05 # теряем здоровье
        if self.hunger >= 60 and self.thirst >= 60:
            if self.hunger >= 80 and self.thirst >= 80:
                regen = 0.01 # быстрая регенерация
            else:
                regen = 0.005 # медленная
            self.health = min(100, self.health + regen)
        if self.health <= 0:
            self.alive = False
            self.health = 0
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def get_tool(self, tool_type):
        """Возвращает ID инструмента указанного типа (для крафта)"""
        from game.items.registry import ITEMS
        for stack in self.inventory_slots:
            if not stack:
                continue
            item = ITEMS.get(stack.item_id)
            if item and isinstance(item, Tool) and item.tool_type == tool_type:
                return stack.item_id
        return None

    def get_stack(self, item_id):
        """Возвращает стопку предмета"""
        return self._get_stack_in_slot(item_id)

    def consume_tool_durability(self, item_id):
        """
        Уменьшает прочность инструмента на 1.
        Если прочность стала 0 - удаляет инструмент.
        Возвращает True если успешно, False если предмет не найден
        """
        for i, stack in enumerate(self.inventory_slots):
            if not stack or stack.item_id != item_id:
                continue
            if not stack.is_tool:
                return False
            stack.durability -= 1
            from game.items.registry import ITEMS
            prototype = ITEMS.get(item_id)
            if prototype and hasattr(prototype, 'tool_type') and prototype.tool_type == 'gun':
                if stack.durability < 0:
                    stack.durability = 0
                return True
            if stack.durability <= 0:
                self.inventory_slots[i] = None
                if self.active_item_id == item_id:
                    self.active_item_id = None
                self.clean_hotbar()
            return True
        return False

    def draw(self, surface, camera_x=0, camera_y=0):
        """Отрисовывает игрока на экране с учётом камеры"""
        from game.assets.sprites import blit_entity
        blit_entity(surface, "player", self.x, self.y, self.size, camera_x, camera_y)