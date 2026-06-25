import pygame
import random
import math
import game.settings as gs
from pygame import K_ESCAPE
from game.story.prologue import PrologueScene
from game.story.pilot_rescue import PilotRescueEpisode
from game.story.captain_rescue import CaptainRescueEpisode
from game.entities.wolf import StoryWolf
from game.entities.bear import StoryBear
from game.items.registry import ITEMS
from game.settings import WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, CRASH_SITE_RADIUS
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
from game.systems.mining import (
    can_mine_structure,
    get_mining_damage,
    uses_tool_durability,
    get_melee_tool_damage,
)

class GameScene:
    def __init__(self, data=None):
        self.player = Player()
        self.tutorial_completed = False
        self.prologue_completed = False
        self.pilot_rescue_completed = False
        self.captain_rescue_completed = False
        self.unlocked_story_recipes = []
        if data:
            if "player" in data:
                self.player.__dict__.update(data["player"])
            self.tutorial_completed = data.get("tutorial_completed", False)
            self.prologue_completed = data.get("prologue_completed", False)
            self.pilot_rescue_completed = data.get("pilot_rescue_completed", False)
            self.captain_rescue_completed = data.get("captain_rescue_completed", False)
            self.unlocked_story_recipes = list(data.get("unlocked_story_recipes", []))
            self._prologue_spawn = (
                data.get("spawn_x"),
                data.get("spawn_y"),
            )
        else:
            self._prologue_spawn = (None, None)

        self.camera = Camera(WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT)
        self.day_night = DayNightCycle()
        self.environment = WorldEnvironment(WORLD_WIDTH, WORLD_HEIGHT)

        if self.prologue_completed:
            sx, sy = self._prologue_spawn
            if sx is not None and sy is not None:
                self.player.x, self.player.y = sx, sy
            else:
                self.player.x, self.player.y = self.environment.get_game_spawn_after_prologue()

        self.pilot_rescue = None
        if self.prologue_completed and not self.pilot_rescue_completed:
            self.pilot_rescue = PilotRescueEpisode(
                self.environment, self.player.x, self.player.y
            )
        elif self.pilot_rescue_completed:
            self.pilot_rescue = PilotRescueEpisode.from_completed(self.environment)

        self.captain_rescue = None
        if self.pilot_rescue_completed and not self.captain_rescue_completed and self.pilot_rescue:
            self.captain_rescue = CaptainRescueEpisode(
                self.environment, self.pilot_rescue.pilot
            )
        elif self.captain_rescue_completed and self.pilot_rescue:
            self.captain_rescue = CaptainRescueEpisode.from_completed(
                self.environment, self.pilot_rescue.pilot
            )
        self._sync_raft_recipe_unlock()

        self.structures = self.environment.generate_structures()
        self.beach_wreckages = self.environment.generate_beach_wreckage()

        self.hud = HUD()
        self.renderer = WorldRenderer(self.environment, self.hud)

        self.enemies = []

        self.projectiles = []

        self.build_mode = False
        self.build_item = None
        self.build_options = ["campfire_kit", "wood_wall_kit", "wood_door_kit"]

        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load("assets/music/les.mp3")
                pygame.mixer.music.set_volume(gs.SOUND_VOLUME)  # громкость 0–1
                pygame.mixer.music.play(-1)  # -1 = бесконечный повтор
            except Exception as e:
                print(f"Не удалось загрузить музыку: {e}")




        def find_grass_pos(max_attempts=200):
            """Возвращает (x, y) на траве или None, если не найдено."""
            for _ in range(max_attempts):
                x = random.randint(0, WORLD_WIDTH)
                y = random.randint(0, WORLD_HEIGHT)
                if self.environment.get_tile(x, y) == 'grass':
                    return x, y
            return None

            # ---------- ВОЛКИ (10 штук) ----------

        for _ in range(10):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Wolf(*pos))


        for _ in range(8):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Bear(*pos))

            # ---------- ОЛЕНИ (20 штук) ----------
        for _ in range(12):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Deer(*pos))


        for _ in range(35):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Rabbit(*pos))

            # ---------- ЛИСЫ (10 штук) ----------
        for _ in range(16):
            pos = find_grass_pos()
            if pos:
                self.enemies.append(Fox(*pos))

            # ---------- ЛУТ: ягоды и камушки ----------
        self.loots = list(self.environment.generate_berry_loots())
        self.loots.extend(self.environment.generate_pebble_loots())



        self.survivors = []
        if not self.pilot_rescue:
            for _ in range(5):
                pos = find_grass_pos()
                if pos:
                    self.survivors.append(Survivor(*pos))




    def _try_start_captain_episode(self):
        if self.captain_rescue or self.captain_rescue_completed:
            return
        if not self.pilot_rescue_completed or not self.pilot_rescue:
            return
        self.captain_rescue = CaptainRescueEpisode(
            self.environment, self.pilot_rescue.pilot
        )

    def _sync_raft_recipe_unlock(self):
        if self.captain_rescue_completed and "raft" not in self.unlocked_story_recipes:
            self.unlocked_story_recipes.append("raft")

    def _finish_captain_rescue_episode(self):
        if self.captain_rescue_completed:
            return
        self.captain_rescue_completed = True
        self._sync_raft_recipe_unlock()

    def _episode_enemies(self):
        enemies = []
        if self.pilot_rescue:
            enemies.extend(self.pilot_rescue.get_combat_wolves())
        if self.captain_rescue:
            enemies.extend(self.captain_rescue.get_combat_bears())
        return enemies

    def _all_combat_enemies(self):
        return self.enemies + self._episode_enemies()

    def _visible_survivors(self):
        survivors = []
        if self.pilot_rescue:
            survivors.extend(self.pilot_rescue.get_draw_survivors())
        if self.captain_rescue and self.captain_rescue.should_render(self.player):
            for s in self.captain_rescue.get_draw_survivors():
                if s not in survivors:
                    survivors.append(s)
        if self.pilot_rescue and self.pilot_rescue.completed:
            survivors.extend(self.survivors)
        elif not self.pilot_rescue:
            survivors.extend(self.survivors)
        return survivors

    def _on_projectile_hit(self, enemy):
        if self.pilot_rescue and isinstance(enemy, StoryWolf):
            self.pilot_rescue.on_wolf_hit()
        if self.captain_rescue and isinstance(enemy, StoryBear):
            self.captain_rescue.on_bear_hit()

    def _any_story_dialog_active(self):
        if self.pilot_rescue and self.pilot_rescue.dialog_active:
            return True
        if self.captain_rescue and self.captain_rescue.dialog_active:
            return True
        return False

    def handle_event(self, event):
        if self.pilot_rescue and self.pilot_rescue.handle_event(event):
            if self.pilot_rescue.completed:
                self.pilot_rescue_completed = True
                self._try_start_captain_episode()
            return self
        if self.captain_rescue and self.captain_rescue.handle_event(event):
            if self.captain_rescue.completed:
                self._finish_captain_rescue_episode()
            return self

        if event.type == pygame.KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.mixer.music.stop()
                from game.scenes.menu import MenuScene
                return MenuScene()
            if event.key == pygame.K_F5:
                save_game(self)
            if event.key == pygame.K_i:
                from game.scenes.inventory_scene import InventoryScene
                return InventoryScene(self.player, self)
            if event.key == pygame.K_e:
                if self.captain_rescue and self.captain_rescue.try_start_captain_dialog(self.player):
                    return self
                if self.pilot_rescue and self.pilot_rescue.try_start_dialog(self.player):
                    return self
                self.player.interact(self.structures)
            if event.key == pygame.K_b:
                # Циклическое переключение строительных наборов
                available = [item for item in self.build_options if self.player.count_item(item) > 0]
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
                    pistol_stack = self.player.get_stack("pistol")
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
                    if self.player.count_item(self.build_item) == 0:
                        available = [item for item in self.build_options if self.player.count_item(item) > 0]
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
                                tool_id = self.player.active_item_id
                                tool_item = ITEMS.get(tool_id) if tool_id else None

                                if not can_mine_structure(s.type, tool_item):
                                    return self

                                damage = get_mining_damage(s.type, tool_item)
                                if damage <= 0:
                                    return self

                                stack = self.player.get_stack(tool_id) if tool_id else None
                                if tool_item and uses_tool_durability(s.type, tool_item):
                                    if not stack or stack.durability is None or stack.durability <= 0:
                                        return self

                                s.health -= damage
                                s.hit_timer = 5

                                if tool_item and uses_tool_durability(s.type, tool_item):
                                    self.player.consume_tool_durability(tool_id)

                                if s.health <= 0:
                                    if s.type == "tree":
                                        for _ in range(random.randint(2, 3)):
                                            self.loots.append(Loot(
                                                s.x + random.randint(-10, 10),
                                                s.y + random.randint(-10, 10), "wood",
                                            ))
                                    elif s.type == "stone_vein":
                                        for _ in range(random.randint(2, 4)):
                                            self.loots.append(Loot(
                                                s.x + random.randint(-10, 10),
                                                s.y + random.randint(-10, 10), "stone",
                                            ))
                                    self.structures.remove(s)
                            return self

                shot = perform_attack(self.player, self._all_combat_enemies(), mouse_pos,
                                      self.camera, self.projectiles)
                if shot:
                    if self.pilot_rescue:
                        self.pilot_rescue.on_player_shot()
                    if self.captain_rescue:
                        self.captain_rescue.on_player_shot(self.player)
                    return self

                tool_id = self.player.active_item_id
                tool_item = ITEMS.get(tool_id) if tool_id else None
                melee_damage = get_melee_tool_damage(tool_item)
                if melee_damage is not None:
                    stack = self.player.get_stack(tool_id)
                    if stack and stack.durability and stack.durability > 0:
                        self.player.attack(self._all_combat_enemies(), mouse_pos, damage=melee_damage)
                        self.player.consume_tool_durability(tool_id)
                        if self.captain_rescue:
                            self.captain_rescue.on_player_attack(self.player)
                    return self

                self.player.attack(self._all_combat_enemies(), mouse_pos)
                if self.captain_rescue:
                    self.captain_rescue.on_player_attack(self.player)
                return self

    def update(self):
        if not self.player.alive:
            from game.scenes.game_over_scenes import GameOverScene
            return GameOverScene()

        keys = pygame.key.get_pressed()
        if not self._any_story_dialog_active():
            self.player.move(keys, self.structures + self.beach_wreckages)
        self.player.update()

        px = self.player.x + self.player.size // 2
        py = self.player.y + self.player.size // 2
        if self.environment.is_near_crash_site(px, py, CRASH_SITE_RADIUS):
            return PrologueScene(revisit=True, player=self.player, game_scene=self)

        if self.pilot_rescue:
            if not self.pilot_rescue.completed:
                self.pilot_rescue.update(
                    self.player, self.structures + self.beach_wreckages, self.environment
                )
            else:
                self.pilot_rescue.pilot.update()

        if self.pilot_rescue and self.pilot_rescue.completed and not self.pilot_rescue_completed:
            self.pilot_rescue_completed = True
            self._try_start_captain_episode()
        elif self.pilot_rescue_completed and not self.captain_rescue and not self.captain_rescue_completed:
            self._try_start_captain_episode()

        if self.captain_rescue and not self.captain_rescue.completed:
            self.captain_rescue.update(
                self.player, self.structures + self.beach_wreckages, self.environment
            )
            if self.captain_rescue.completed:
                self._finish_captain_rescue_episode()
        elif self.captain_rescue:
            self.captain_rescue.captain.update()

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

        if self.environment.is_near_crash_site(px, py, CRASH_SITE_RADIUS):
            pygame.mixer.music.stop()
            return PrologueScene(revisit=True, player=self.player, game_scene=self)

        if not self.player.alive:
            pygame.mixer.music.stop()  # <-- Останавливаем музыку
            from game.scenes.game_over_scenes import GameOverScene
            return GameOverScene()



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
            proj.update(
                self._all_combat_enemies(),
                self.structures + self.beach_wreckages,
                on_enemy_hit=self._on_projectile_hit,
            )
            if not proj.active:
                self.projectiles.remove(proj)
        self.hud.update(self.player.health)

    def draw(self, screen):
        # Сначала рендерим мир через WorldRenderer
        self.renderer.render_full(
            screen, self.camera, self.player,
            self.enemies, self.loots, self._visible_survivors(),
            self.day_night, self.structures

        )
        self.hud.draw(screen, self.player)

        if self.pilot_rescue:
            self.pilot_rescue.draw_footprints(screen, self.camera)
        for wreck in self.beach_wreckages:
            wreck.draw(screen, self.camera.x, self.camera.y)

        for proj in self.projectiles:
            proj.draw(screen, self.camera.x, self.camera.y)

        if self.captain_rescue:
            self.captain_rescue.draw_bears(screen, self.camera)
            self.captain_rescue.draw_hint(screen, self.player, self.camera)
            self.captain_rescue.draw_dialog(screen)

        if self.pilot_rescue:
            for wolf in self.pilot_rescue.wolves:
                wolf.draw(screen, self.camera.x, self.camera.y)
            self.pilot_rescue.draw_hint(screen)
            self.pilot_rescue.draw_dialog(screen)

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