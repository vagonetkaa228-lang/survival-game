import pygame
from game.settings import WIDTH, HEIGHT, BLUE, WORLD_WIDTH, WORLD_HEIGHT
from game.items.tool import Tool
from game.items.item_stack import ItemStack
import math

class Player:
    def __init__(self):
        self.x = WIDTH// 2
        self.y = HEIGHT//2
        self.speed = 2
        self.size = 20
        self.hunger = 100
        self.thirst = 100
        self.health = 100
        self.inventory = {}
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.attack_cooldown = 0
        self.attack_range = 50
        self.attack_damage = 25
        self.attack_timer = 0  # таймер анимации удара (кадры)
        self.attack_angle = 0 # направление удара (можно по мыши)
        self.alive = True
        self.inventory = {}  # ключ: item_id, значение: количество
        self.selected_item = None  # текущий выбранный предмет (для быстрого использования)
        self.hotbar = [None] * 5
        self.active_item_id = None
        self.energy = 100
        self.max_energy = 100
        self.walk_speed = 2
        self.run_speed = 5

    def clean_hotbar(self):
        """Убирает из хотбара предметы, которых нет в инвентаре"""
        for i in range(len(self.hotbar)):
            item_id = self.hotbar[i]
            if item_id is not None and item_id not in self.inventory:
                self.hotbar[i] = None
        # Сбрасываем активный предмет, если его больше нет
        if self.active_item_id is not None and self.active_item_id not in self.inventory:
            self.active_item_id = None

    def count_item(self, item_id):
        """Вернуть общее количество предмета (независимо от прочности)"""
        stack = self.inventory.get(item_id)
        return stack.count if stack else 0

    def set_hotbar_slot(self, index, item_id):
        if 0 <= index < len(self.hotbar):
            self.hotbar[index] = item_id

    def get_hotbar_item(self, index):
        if 0 <= index < len(self.hotbar):
            return self.hotbar[index]
        return None

    def use_hotbar_item(self, index):
        item_id = self.get_hotbar_item(index)
        self.active_item_id = item_id  # теперь пустой слот делает руки пустыми
        if item_id is None:
            return
        from game.items.registry import ITEMS
        item = ITEMS.get(item_id)
        if item:
            if hasattr(item, 'hunger_restore') or hasattr(item, 'thirst_restore'):
                self.use_item(item_id)  # еда/вода сразу используется

    def add_item(self, item_id, amount=1, durability=None):
        """
        Добавляет предмет в инвентарь.
        Если durability не задана, для инструментов берётся максимальная прочность.
        Возвращает True, если хотя бы часть предмета поместилась, иначе False.
        """
        from game.items.registry import ITEMS
        prototype = ITEMS.get(item_id)
        if not prototype:
            return False

        # --- уже есть такой предмет в инвентаре ---
        if item_id in self.inventory:
            stack = self.inventory[item_id]

            # Инструменты не стакаются (max_stack == 1)
            if prototype.max_stack == 1:
                # Если это инструмент, вернём False – нельзя иметь два
                return False

            # Стакаемый предмет
            new_total = stack.count + amount
            if new_total <= prototype.max_stack:
                stack.count = new_total
                return True
            else:
                stack.count = prototype.max_stack
                return False  # полностью не влезло, но старый стек полон

        # --- предмета в инвентаре ещё нет ---
        else:
            self.inventory[item_id] = ItemStack(item_id, amount, durability)
            success = True

        # Если добавили инструмент или оружие – сразу кладём в хотбар
        if success:
            item = ITEMS.get(item_id)
            if item and hasattr(item, 'tool_type'):
                self.add_to_hotbar(item_id)

        return success


    def remove_item(self, item_id, amount=1):
        """Удаляет количество предмета, чистит хотбар, возвращает успех"""
        stack = self.inventory.get(item_id)
        if not stack or stack.count < amount:
            return False
        stack.count -= amount
        if stack.count <= 0:
            del self.inventory[item_id]
        self.clean_hotbar()
        return True

    def obtain_pistol(self):
        """Подобрать пистолет или патроны, если пистолет уже есть."""
        if "pistol" in self.inventory:
            # Уже есть пистолет: получаем только боеприпасы
            self.add_item("magazine", 8)
        else:
            # Первый пистолет – оружие с полным магазином
            self.add_item("pistol", 1, durability=8)
            self.add_to_hotbar("pistol")

    def use_item(self, item_id):
        """Использует предмет (еда/вода). Для инструментов не вызывается."""
        from game.items.registry import ITEMS
        if item_id not in self.inventory or item_id not in ITEMS:
            return False
        item = ITEMS[item_id]
        if hasattr(item, 'hunger_restore') or hasattr(item, 'thirst_restore'):
            if item.use(self):
                return self.remove_item(item_id, 1)
        return False

    def add_to_hotbar(self, item_id):
        """Добавляет предмет в хотбар, если его там ещё нет"""
        if item_id is None:
            return
        # Если уже есть в хотбаре – просто делаем активным
        for i in range(len(self.hotbar)):
            if self.hotbar[i] == item_id:
                self.active_item_id = item_id
                return
        # Ищем свободный слот
        for i in range(len(self.hotbar)):
            if self.hotbar[i] is None:
                self.hotbar[i] = item_id
                self.active_item_id = item_id
                return
        # Если нет свободных – заменяем первый слот
        self.hotbar[0] = item_id
        self.active_item_id = item_id

    def attack(self, enemies, mouse_pos=None):
        if self.attack_cooldown > 0 or not self.alive:
            return
        if self.attack_cooldown > 0:
            return

        if mouse_pos:
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            self.attack_angle = math.atan2(dy, dx)
        else:
            self.attack_angle = 0

        self.attack_timer = 10

        for e in enemies:
            dx = e.x - self.x
            dy = e.y - self.y
            dist = math.hypot(dx, dy)
            if dist < self.attack_range:
                e.health -= self.attack_damage
                e.hit_timer = 5  # ← запускаем эффект удара
                e.aggro_player = True

        self.attack_cooldown = 30

    def move(self, keys, structures):
        if not self.alive:
            return

        # Определяем скорость
        if keys[pygame.K_LSHIFT] and self.energy > 0:
            current_speed = self.run_speed
            self.energy = max(0, self.energy - 0.3)  # расход энергии за кадр
        else:
            current_speed = self.walk_speed
            self.energy = min(100, self.energy + 0.1)  # восстановление

        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= current_speed
        if keys[pygame.K_s]: dy += current_speed
        if keys[pygame.K_a]: dx -= current_speed
        if keys[pygame.K_d]: dx += current_speed

        # Проверка коллизий по X
        new_x = self.x + dx
        player_rect = pygame.Rect(new_x, self.y, self.size, self.size)
        for s in structures:
            if s.solid and player_rect.colliderect(s.get_rect()):
                if dx > 0:
                    new_x = s.x - self.size
                elif dx < 0:
                    new_x = s.x + s.width
                break
        # Проверка по Y
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
        """Взаимодействие с ближайшей дверью"""
        if not self.alive:
            return
        interaction_range = 50  # дистанция взаимодействия
        for s in structures:
            if s.type == "door":
                # Вычисляем расстояние до центра двери
                door_center_x = s.x + s.width // 2
                door_center_y = s.y + s.height // 2
                dist = math.hypot(self.x + self.size // 2 - door_center_x,
                                  self.y + self.size // 2 - door_center_y)
                if dist <= interaction_range:
                    s.toggle()
                    break  # переключаем только одну ближайшую дверь

    def update(self):
        if not self.alive:
            return
        self.hunger -= 0.001
        self.thirst -= 0.002
        if self.hunger <= 0 or self.thirst <= 0:
            self.health -= 0.05

        # Регенерация при высоких показателях
        if self.hunger >= 60 and self.thirst >= 60:
            if self.hunger >= 80 and self.thirst >= 80:
                regen = 0.01  # ~6 HP/сек при 60 FPS
            else:
                regen = 0.005  # ~3 HP/сек
            self.health = min(100, self.health + regen)

        if self.health <= 0:
            self.alive = False
            self.health = 0
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def get_tool(self, tool_type):
        """Возвращает item_id первого инструмента заданного типа (если есть)"""
        from game.items.registry import ITEMS
        for item_id, stack in self.inventory.items():
            if item_id in ITEMS:
                item = ITEMS[item_id]
                if isinstance(item, Tool) and item.tool_type == tool_type:
                    return item_id
        return None

    def consume_tool_durability(self, item_id):
        stack = self.inventory.get(item_id)
        if not stack or not stack.is_tool:
            return False
        stack.durability -= 1

        # для пистолета не удаляем, для остальных удаляем при 0
        from game.items.registry import ITEMS
        prototype = ITEMS.get(item_id)
        if prototype and hasattr(prototype, 'tool_type') and prototype.tool_type == 'gun':
            if stack.durability < 0:
                stack.durability = 0
            return True

        if stack.durability <= 0:
            self.remove_item(item_id, 1)
            if self.active_item_id == item_id:
                self.active_item_id = None
        return True

    def draw(self, surface):
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.size, self.size))

