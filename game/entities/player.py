import pygame
from game.settings import WIDTH, HEIGHT, BLUE, WORLD_WIDTH, WORLD_HEIGHT
from game.items.tool import Tool
from game.items.item_stack import ItemStack
import math

INVENTORY_SIZE = 20


class Player:
    def __init__(self):
        self.x = WIDTH// 2
        self.y = HEIGHT//2
        self.speed = 2  #2
        self.size = 40
        self.hunger = 100
        self.thirst = 100
        self.health = 100
        self.x = WORLD_WIDTH // 2
        self.y = WORLD_HEIGHT // 2
        self.attack_cooldown = 0
        self.attack_range = 50
        self.attack_damage = 25
        self.attack_timer = 0  # таймер анимации удара (кадры)
        self.attack_angle = 0 # направление удара (можно по мыши)
        self.alive = True
        self.inventory_slots = [None] * INVENTORY_SIZE
        self.selected_item = None
        self.hotbar = [None] * 5
        self.active_item_id = None
        self.energy = 100
        self.max_energy = 100
        self.walk_speed = 2
        self.run_speed = 4

    def _find_empty_slot(self):
        for i, slot in enumerate(self.inventory_slots):
            if slot is None:
                return i
        return None

    def _get_stack_in_slot(self, item_id):
        for stack in self.inventory_slots:
            if stack and stack.item_id == item_id:
                return stack
        return None

    def has_item(self, item_id):
        return self.count_item(item_id) > 0

    def clean_hotbar(self):
        for i in range(len(self.hotbar)):
            item_id = self.hotbar[i]
            if item_id is not None and not self.has_item(item_id):
                self.hotbar[i] = None
        if self.active_item_id is not None and not self.has_item(self.active_item_id):
            self.active_item_id = None

    def count_item(self, item_id):
        return sum(
            stack.count for stack in self.inventory_slots
            if stack and stack.item_id == item_id
        )

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
        from game.items.registry import ITEMS
        prototype = ITEMS.get(item_id)
        if not prototype:
            return False

        remaining = amount
        added_any = False
        max_stack = prototype.max_stack

        if max_stack == 1:
            while remaining > 0:
                slot_idx = self._find_empty_slot()
                if slot_idx is None:
                    break
                self.inventory_slots[slot_idx] = ItemStack(item_id, 1, durability)
                remaining -= 1
                added_any = True
        else:
            for stack in self.inventory_slots:
                if stack and stack.item_id == item_id and stack.count < max_stack:
                    can_add = min(remaining, max_stack - stack.count)
                    stack.count += can_add
                    remaining -= can_add
                    added_any = True
                    if remaining <= 0:
                        break

            while remaining > 0:
                slot_idx = self._find_empty_slot()
                if slot_idx is None:
                    break
                chunk = min(remaining, max_stack)
                self.inventory_slots[slot_idx] = ItemStack(item_id, chunk, durability)
                remaining -= chunk
                added_any = True

        if added_any and hasattr(prototype, 'tool_type'):
            self.add_to_hotbar(item_id)

        return added_any and remaining == 0

    def remove_item(self, item_id, amount=1):
        if self.count_item(item_id) < amount:
            return False
        remaining = amount
        for i, stack in enumerate(self.inventory_slots):
            if not stack or stack.item_id != item_id:
                continue
            take = min(remaining, stack.count)
            stack.count -= take
            remaining -= take
            if stack.count <= 0:
                self.inventory_slots[i] = None
            if remaining <= 0:
                break
        self.clean_hotbar()
        return True

    def obtain_pistol(self):
        if self.has_item("pistol"):
            self.add_item("magazine", 8)
        else:
            self.add_item("pistol", 1, durability=8)
            self.add_to_hotbar("pistol")

    def use_item(self, item_id):
        from game.items.registry import ITEMS
        if not self.has_item(item_id) or item_id not in ITEMS:
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

    def attack(self, enemies, mouse_pos=None, damage=None):
        if self.attack_cooldown > 0 or not self.alive:
            return

        hit_damage = damage if damage is not None else self.attack_damage

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
                e.health -= hit_damage
                e.hit_timer = 5
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
        self.hunger -= 0.008
        self.thirst -= 0.009
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
        from game.items.registry import ITEMS
        for stack in self.inventory_slots:
            if not stack:
                continue
            item = ITEMS.get(stack.item_id)
            if item and isinstance(item, Tool) and item.tool_type == tool_type:
                return stack.item_id
        return None

    def get_stack(self, item_id):
        return self._get_stack_in_slot(item_id)

    def consume_tool_durability(self, item_id):
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
        from game.assets.sprites import blit_entity
        blit_entity(surface, "player", self.x, self.y, self.size, camera_x, camera_y)

