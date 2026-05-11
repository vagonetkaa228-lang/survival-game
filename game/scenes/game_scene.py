import pygame
import random
import math
from pygame import K_ESCAPE
from game.items.registry import ITEMS
from game.settings import WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from game.entities.player import Player
from game.entities.loot import Loot
from game.entities.survivor import Survivor
from game.save_system import save_game
from game.systems.camera import Camera
from game.systems.environment import DayNightCycle, WorldEnvironment
from game.systems.hud import HUD
from game.systems.render import WorldRenderer
from game.entities import Wolf, Bear, Structure, Deer, Rabbit, Fox
from game.systems.combat import perform_attack

class GameScene:
    def __init__(self, data=None):
        self.player = Player()
        if data:
            if data:
                self.player.__dict__.update(data["player"])


        self.camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        self.day_night = DayNightCycle()
        self.environment = WorldEnvironment(WORLD_WIDTH, WORLD_HEIGHT)


        self.structures = self.environment.generate_structures()

        self.hud = HUD()
        self.renderer = WorldRenderer(self.environment, self.hud)

        self.enemies = []

        self.projectiles = []

        self.build_mode = False
        self.build_item = None
        self.build_options = ["campfire_kit", "wood_wall_kit", "wood_door_kit"]

        def find_grass_pos(max_attempts=200):
            """Возвращает (x, y) на траве или None, если не найдено."""
            for _ in range(max_attempts):
                x = random.randint(0, WORLD_WIDTH)
                y = random.randint(0, WORLD_HEIGHT)
                if self.environment.get_tile(x, y) == 'grass':
                    return x, y
            return None

            # ---------- ВОЛКИ (10 штук) ----------

        for _ in range(1):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Wolf(*pos))

            # ---------- МЕДВЕДИ (15 штук) ----------
        for _ in range(1):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Bear(*pos))

            # ---------- ОЛЕНИ (20 штук) ----------
        for _ in range(2):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Deer(*pos))

            # ---------- КРОЛИКИ (100 штук) ----------
        for _ in range(1):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Rabbit(*pos))

            # ---------- ЛИСЫ (10 штук) ----------
        for _ in range(10):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Fox(*pos))

            # ---------- ЛУТ (ягоды, вода, дерево, камень) ----------
        self.loots = []
        for _ in range(100):
            for _ in range(30):  # попытки найти сушу (траву или песок)
                x = random.randint(0, WORLD_WIDTH)
                y = random.randint(0, WORLD_HEIGHT)
                if self.environment.is_land(x, y):
                    break
            else:
                continue
            item_id = random.choice(["berry", "clean_water", "wood", "stone"])
            self.loots.append(Loot(x, y, item_id))

        # ---------- ВЫЖИВШИЕ (5 человек) ----------
        self.survivors = []
        for _ in range(5):
            pos = find_grass_pos()
            if pos:
                self.survivors.append(Survivor(*pos))

        # ---------- ПИСТОЛЕТЫ (5 штук, только на суше) ----------
        for _ in range(5):
            for _ in range(30):
                x = random.randint(0, WORLD_WIDTH)
                y = random.randint(0, WORLD_HEIGHT)
                if self.environment.is_land_fast(x, y):  # достаточно эллипса (без шума)
                    break
            else:
                continue
            self.loots.append(Loot(x, y, "pistol"))

        # for _ in range(10):
        #     self.enemies.append(Wolf(random.randint(0, WORLD_WIDTH-random.randint(500,1000)), random.randint(0, WORLD_HEIGHT-random.randint(500,1000))))
        # for _ in range(10):
        #     self.enemies.append(Bear(random.randint(0, WORLD_WIDTH-random.randint(100,1000)), random.randint(0, WORLD_HEIGHT - random.randint(100,1000))))
        #
        # for _ in range(10):
        #     self.enemies.append(Deer(random.randint(0, WORLD_WIDTH-random.randint(100,1000)), random.randint(0, WORLD_HEIGHT - random.randint(100,1000))))
        # for _ in range(10):
        #     self.enemies.append(Rabbit(random.randint(0, WORLD_WIDTH-random.randint(100,1000)), random.randint(0, WORLD_HEIGHT - random.randint(100,1000))))
        # for _ in range(10):
        #     self.enemies.append(Fox(random.randint(0, WORLD_WIDTH -random.randint(100,1000)), random.randint(0, WORLD_HEIGHT - random.randint(100,1000))))
        #
        # self.loots = []
        # for _ in range(10):  # меньше предметов
        #     for attempt in range(10):  # больше 10 попыток не делаем
        #         x = random.randint(0, WORLD_WIDTH)
        #         y = random.randint(0, WORLD_HEIGHT)
        #         if self.environment.is_land(x, y):
        #             break
        #     else:
        #         continue  # пропускаем предмет, если не нашли сушу
        #     item_id = random.choice(["berry", "clean_water", "wood", "stone"])
        #     self.loots.append(Loot(x, y, item_id))
        # self.survivors = [Survivor(random.randint(0, WORLD_WIDTH), random.randint(0, WORLD_HEIGHT)) for _ in range(5)]
        #
        # for _ in range(5):  # несколько штук
        #     for _ in range(30):  # до 30 попыток
        #         x = random.randint(0, WORLD_WIDTH)
        #         y = random.randint(0, WORLD_HEIGHT)
        #         if self.environment.is_land_fast(x, y):
        #             break
        #     else:
        #         continue  # не нашли место — пропускаем этот пистолет
        #     self.loots.append(Loot(x, y, "pistol"))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                from game.scenes.menu import MenuScene
                return MenuScene()
            if event.key == pygame.K_F5:
                save_game(self.player)
            if event.key == pygame.K_i:
                from game.scenes.inventory_scene import InventoryScene
                return InventoryScene(self.player, self)
            if event.key == pygame.K_e:
                self.player.interact(self.structures)
            if event.key == pygame.K_b:
                # Циклическое переключение строительных наборов
                available = [item for item in self.build_options if self.player.inventory.get(item, 0) > 0]
                if not available:
                    self.build_mode = False
                    self.build_item = None
                else:
                    if not self.build_mode:
                        self.build_mode = True
                        self.build_item = available[0]
                    else:
                        current_idx = available.index(self.build_item) if self.build_item in available else -1
                        next_idx = (current_idx + 1) % len(available)
                        self.build_item = available[next_idx]
                return self
            if event.key == pygame.K_n:
                if self.build_mode:
                    self.build_mode = False
                    self.build_item = None
                    return self
            if event.key == pygame.K_1:
                self.player.use_hotbar_item(0)
                return self
            if event.key == pygame.K_2:
                self.player.use_hotbar_item(1)
                return self
            if event.key == pygame.K_3:
                self.player.use_hotbar_item(2)
                return self
            if event.key == pygame.K_4:
                self.player.use_hotbar_item(3)
                return self
            if event.key == pygame.K_5:
                self.player.use_hotbar_item(4)
                return self
            if event.key == pygame.K_r:
                if self.player.active_item_id == "pistol":
                    pistol_stack = self.player.inventory.get("pistol")
                    if pistol_stack and pistol_stack.durability == 0:
                        if self.player.count_item("magazine") > 0:
                            self.player.remove_item("magazine", 1)
                            pistol_stack.durability = 8  # полный магазин
                return self

        self.camera.handle_zoom(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.build_mode and self.build_item:
                # Размещение объекта
                mouse_x, mouse_y = pygame.mouse.get_pos()
                world_x = mouse_x / self.camera.zoom + self.camera.x
                world_y = mouse_y / self.camera.zoom + self.camera.y
                grid_size = 40
                grid_x = round(world_x / grid_size) * grid_size
                grid_y = round(world_y / grid_size) * grid_size

                can_place = True
                new_rect = pygame.Rect(grid_x, grid_y, grid_size, grid_size)
                for s in self.structures:
                    if s.get_rect().colliderect(new_rect):
                        can_place = False
                        break

                if can_place:
                    self.player.remove_item(self.build_item, 1)
                    if self.build_item == "campfire_kit":
                        self.structures.append(Structure(grid_x, grid_y, "campfire", solid=False))
                    elif self.build_item == "wood_wall_kit":
                        self.structures.append(Structure(grid_x, grid_y, "wall", solid=True))
                    elif self.build_item == "wood_door_kit":
                        self.structures.append(Structure(grid_x, grid_y, "door", solid=True))
                    # Если предметы кончились, переключить
                    if self.player.inventory.get(self.build_item, 0) == 0:
                        available = [item for item in self.build_options if self.player.inventory.get(item, 0) > 0]
                        if available:
                            self.build_item = available[0]
                        else:
                            self.build_mode = False
                            self.build_item = None

            if not self.build_mode:
                mouse_pos = pygame.mouse.get_pos()
                world_click_x = mouse_pos[0] / self.camera.zoom + self.camera.x
                world_click_y = mouse_pos[1] / self.camera.zoom + self.camera.y

                # 1) Сначала пробуем добычу ресурсов
                for s in self.structures[:]:
                    if s.type in ("tree", "stone_vein"):
                        if s.get_rect().collidepoint(world_click_x, world_click_y):
                            player_center_x = self.player.x + self.player.size // 2
                            player_center_y = self.player.y + self.player.size // 2
                            struct_center_x = s.x + s.width // 2
                            struct_center_y = s.y + s.height // 2
                            dist = math.hypot(player_center_x - world_click_x, player_center_y - world_click_y)
                            if dist <= 150:
                                tool_type = "axe" if s.type == "tree" else "pickaxe"
                                tool_id = self.player.active_item_id
                                tool_item = ITEMS.get(tool_id) if tool_id else None

                                # Урон по умолчанию (кулаками)
                                damage = 1
                                tool_used = False

                                if tool_item and hasattr(tool_item, 'tool_type') and tool_item.tool_type == tool_type:
                                    stack = self.player.inventory.get(tool_id)
                                    if stack and stack.durability is not None and stack.durability > 0:
                                        damage = 3  # бонус инструментом
                                        tool_used = True

                                s.health -= damage
                                s.hit_timer = 5

                                if tool_used:
                                    self.player.consume_tool_durability(tool_id)  # <-- трата прочности

                                # if dist <= 150:
                            #     tool_type = "axe" if s.type == "tree" else "pickaxe"
                            #     tool_id = self.player.active_item_id
                            #     tool_item = ITEMS.get(tool_id) if tool_id else None
                            #     if tool_item and hasattr(tool_item, 'tool_type') and tool_item.tool_type == tool_type:
                            #         damage = 2  # бонус, если в руке подходящий инструмент
                            #     else:
                            #         damage = 1
                            #     damage = 2 if tool_id else 1
                            #     s.health -= damage
                            #     s.hit_timer = 5  # подсветка
                                if s.health <= 0:
                                    if s.type == "tree":
                                        for _ in range(random.randint(2, 3)):
                                            self.loots.append(Loot(s.x + random.randint(-10, 10),
                                                                   s.y + random.randint(-10, 10), "wood"))
                                    elif s.type == "stone_vein":
                                        for _ in range(random.randint(2, 4)):
                                            self.loots.append(Loot(s.x + random.randint(-10, 10),
                                                                   s.y + random.randint(-10, 10), "stone"))
                                    self.structures.remove(s)
                            # нашли структуру – дальше атаку не проводим
                            return self

                if not perform_attack(self.player, self.enemies, mouse_pos,
                                      self.camera, self.projectiles):
                    self.player.attack(self.enemies, mouse_pos)
                return self

    def update(self):
        if not self.player.alive:
            from game.scenes.game_over_scenes import GameOverScene
            return GameOverScene()

        keys = pygame.key.get_pressed()
        self.player.move(keys, self.structures)
        self.player.update()

        self.day_night.update()
        self.camera.update(self.player.x, self.player.y)

        # сбор лута
        for loot in self.loots[:]:
            if pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size).colliderect(
                    pygame.Rect(loot.x, loot.y, loot.size, loot.size)
            ):
                if loot.item_id == "pistol":
                    self.player.obtain_pistol()
                else:
                    self.player.add_item(loot.item_id, 1)
                    # Если подобрали инструмент или оружие – сразу в хотбар
                    item = ITEMS.get(loot.item_id)
                    if item and hasattr(item, 'tool_type'):
                        self.player.add_to_hotbar(loot.item_id)
                self.loots.remove(loot)

        # поиск выживших
        for s in self.survivors:
            if not s.found and pygame.Rect(self.player.x, self.player.y, self.player.size,
                                           self.player.size).colliderect(
                    pygame.Rect(s.x, s.y, s.size, s.size)
            ):
                s.found = True
                print("Вы нашли выжившего!")

        # обновление врагов
        for enemy in self.enemies[:]:
            should_remove = enemy.update(self.player, self.enemies, self.structures, self.environment)
            if should_remove:
                # Дроп
                if isinstance(enemy, Deer) or isinstance(enemy, Bear):
                    for _ in range(3):
                        self.loots.append(
                            Loot(enemy.x + random.randint(-20, 20), enemy.y + random.randint(-20, 20), "meat"))
                elif isinstance(enemy, Rabbit):
                    self.loots.append(Loot(enemy.x, enemy.y, "meat"))
                elif isinstance(enemy, Fox):
                    self.loots.append(Loot(enemy.x, enemy.y, "meat"))
                # elif isinstance(enemy, Bear):
                #     self.loots.append(Loot(enemy.x, enemy.y, "meat"))
                elif isinstance(enemy, Wolf):
                    self.loots.append(Loot(enemy.x, enemy.y, 'meat' ))

                self.enemies.remove(enemy)

        # обновление структур и эффекты
        for s in self.structures:
            if s.hit_timer > 0:
                s.hit_timer -= 1
            if s.type == "campfire":
                center_x = s.x + s.width // 2
                center_y = s.y + s.height // 2
                dist = math.hypot(self.player.x - center_x, self.player.y - center_y)
                if dist < 80:
                    self.player.health = min(100, self.player.health + 0.05)
        # обновление снарядов
        for proj in self.projectiles[:]:
            proj.update(self.enemies, self.structures)
            if not proj.active:
                self.projectiles.remove(proj)
        self.hud.update(self.player.health)

    def draw(self, screen):
        # Сначала рендерим мир через WorldRenderer
        self.renderer.render_full(
            screen, self.camera, self.player,
            self.enemies, self.loots, self.survivors,
            self.day_night, self.structures

        )
        self.hud.draw(screen, self.player)

        for proj in self.projectiles:
            proj.draw(screen, self.camera.x, self.camera.y)

        # Отрисовка призрака постройки
        if self.build_mode and self.build_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_x = mouse_x / self.camera.zoom + self.camera.x
            world_y = mouse_y / self.camera.zoom + self.camera.y
            grid_size = 40
            grid_x = round(world_x / grid_size) * grid_size
            grid_y = round(world_y / grid_size) * grid_size

            if self.build_item == "campfire_kit":
                color = (255, 140, 0, 128)
            elif self.build_item == "wood_wall_kit":
                color = (101, 67, 33, 128)
            elif self.build_item == "wood_door_kit":
                color = (139, 90, 43, 128)
            else:
                color = (150, 150, 150, 128)

            ghost_surf = pygame.Surface((grid_size, grid_size), pygame.SRCALPHA)
            ghost_surf.fill(color)
            screen.blit(ghost_surf, (grid_x - self.camera.x, grid_y - self.camera.y))

            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Строительство: {self.build_item} (B - сменить)", True, (255, 255, 255))
            screen.blit(text, (100, 10))
        # отрисовка снарядов
        for proj in self.projectiles:
            proj.draw(screen, self.camera.x, self.camera.y)

        self.hud.draw(screen, self.player)