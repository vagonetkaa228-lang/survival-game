import pygame
import math
import random
from game.settings import WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, BLACK, WHITE, CRASH_SITE_RADIUS
from game.entities.player import Player
from game.entities.loot import Loot
from game.entities.wolf import WeakWolf
from game.systems.environment import WorldEnvironment
from game.systems.combat import perform_attack
from game.story.helicopter import HelicopterWreckage, StaticWreckage
from game.scenes.inventory_scene import InventoryScene
from game.assets.sprites import get_sprite
import game.settings as gs
class _PrologueCamera:
    zoom = 1
    x = 0
    y = 0

"""На вайб-кожено"""
class _PrologueInventory(InventoryScene):
    def handle_event(self, event):
        result = super().handle_event(event)
        if result is self.game_scene:
            self.game_scene._on_inventory_closed()
        return result


class WreckagePiece:
    def __init__(self, rect):
        self.x = rect.x
        self.y = rect.y
        self.width = rect.width
        self.height = rect.height
        self.rect = rect
        self.solid = True

    def get_rect(self):
        return self.rect


class PrologueScene:
    PICKUP_RADIUS = 45

    def __init__(self, revisit=False, player=None, game_scene=None):
        self.revisit = revisit
        self.game_scene = game_scene

        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)

        self.phase = "revisit" if revisit else "helicopter"
        self.timer = 0

        self.heli_x = WIDTH // 2
        self.heli_y = HEIGHT // 3
        self.heli_phase = "center"
        self.heli_timer = 0.5
        self.center_duration = 28 #Сколько лети 28
        self.descend_duration = 10 #Сколько падает 10

        self.descend_start_x = self.heli_x
        self.descend_start_y = self.heli_y
        self.descend_target_x = WIDTH + 200
        self.descend_target_y = HEIGHT + 200

        self.tree_obstacles = []
        self.crash_alpha = 0
        self.smoke_particles = []

        self.helicopter_channel = None
        if not self.revisit:
            try:
                self.helicopter_sound = pygame.mixer.Sound("assets/music/helicopter.mp3")
                self.helicopter_channel = pygame.mixer.find_channel()
                if self.helicopter_channel:
                    self.helicopter_channel.play(self.helicopter_sound, loops=-1)
                    self.helicopter_channel.set_volume(gs.SOUND_VOLUME)
            except Exception as e:
                print(f"Не удалось загрузить звук вертолёта: {e}")

        self.dialogues = [
            {"time": 4.0, "author": "Пилот", "text": "Далеко ещё до этого острова..."},
            {"time": 9.0, "author": "Капитан", "text": "Скоро. По карте уже близко."},
            {"time": 14.5, "author": "Игрок", "text": "Я надеюсь мы не зря туда летим и мы найдем, что-то важное"},
            {"time": 20.5, "author": "Капитан", "text": "Поверь,там будет на что посмотреть.. "},
            {"time": 25.5, "author": "Пилот", "text": "Осторожно! Что-то с двигателем."},
            {"time": 28.0, "author": "Пилот", "text": "Теряю управление! Держитесь!!!"},
        ]
        self.current_dialogue_index = 0
        self.dialogue_active = False
        self.dialogue_timer = 0
        self.dialogue_duration = 4.0

        # Отдельная карта 1000×1000 — пролог всегда с водой слева и песком на берегу
        self.environment = WorldEnvironment(1000, 1000)
        self.world_environment = WorldEnvironment(WORLD_WIDTH, WORLD_HEIGHT)
        self.spawn_point = (240, 480)
        self.world_offset_x = -150
        self.world_offset_y = 0

        self.helicopter_sprite = None  # будет загружен при первом рисовании

        if player is not None:
            self.player = Player()
            self.player.__dict__.update(player.__dict__)
        else:
            self.player = Player()

        self.footprints = []
        self.show_footprints = False
        self.footprint_trigger_index = 0

        self.trees = []
        self._generate_trees()

        self.fade_out_alpha = 0
        self.wreckages = []

        # --- Геймплей пролога ---
        self.loots = []
        self.wolf = None
        self.wolf_spawn_delay = random.uniform(5.0, 10.0)
        self.wolf_spawn_timer = 0.0
        self.wolf_killed = False
        self.weapon_picked_up = False
        self.projectiles = []
        self.shoot_cooldown = 0
        self._camera = _PrologueCamera()

        self.message = None
        self.message_timer = 0.0
        self.exit_point = (WIDTH - 15, HEIGHT // 2)

        self.wakeup_sub = "explore"

        if self.revisit:
            self._init_revisit()

    def _init_revisit(self):
        self.player.x, self.player.y = self.spawn_point
        self._generate_static_wreckage()
        self.loots = []
        self.wolf = None
        self.show_footprints = False

    def _show_message(self, text, duration=3.0):
        self.message = text
        self.message_timer = duration

    def _spawn_weapon_loot(self):
        cx, cy = self.spawn_point[0] + 60, self.spawn_point[1] - 20
        self.loots.extend([
            Loot(cx, cy, "pistol"),
            Loot(cx + 18, cy + 12, "magazine"),
            Loot(cx - 14, cy + 16, "magazine"),
            Loot(cx + 8, cy - 18, "magazine"),
        ])

    def _spawn_food_loot(self):
        if not self.wreckages:
            return
        sx, sy = self.spawn_point
        nearby = [
            w for w in self.wreckages
            if math.hypot(w.x + w.width // 2 - sx, w.y + w.height // 2 - sy) < 160
        ]
        if not nearby:
            nearby = self.wreckages
        for _ in range(random.randint(4, 6)):
            wreck = random.choice(nearby)
            item_id = "clean_water"
            lx = wreck.x + wreck.width // 2 + random.randint(-12, 12)
            ly = wreck.y + wreck.height // 2 + random.randint(-12, 12)
            lx = max(10, min(WIDTH - 20, lx))
            ly = max(10, min(HEIGHT - 20, ly))
            self.loots.append(Loot(lx, ly, item_id))

    def _screen_tile(self, sx, sy):
        wx = sx + self.world_offset_x
        wy = sy + self.world_offset_y
        return self.environment.get_tile(wx, wy)

    def _spawn_wolf(self):
        px = self.player.x + self.player.size // 2
        py = self.player.y + self.player.size // 2
        candidates = []

        for tx, ty in self.trees:
            for _ in range(3):
                wx = tx + random.randint(-20, 20)
                wy = ty + random.randint(-20, 20)
                wx = max(30, min(WIDTH - 50, wx))
                wy = max(30, min(HEIGHT - 50, wy))
                if self._screen_tile(wx, wy) != 'grass':
                    continue
                dist = math.hypot(wx - px, wy - py)
                if 140 <= dist <= 240:
                    candidates.append((wx, wy))

        if candidates:
            wx, wy = random.choice(candidates)
        else:
            for _ in range(40):
                wx = random.randint(280, WIDTH - 80)
                wy = random.randint(80, HEIGHT // 2)
                if self._screen_tile(wx, wy) == 'grass':
                    dist = math.hypot(wx - px, wy - py)
                    if dist >= 120:
                        break
            else:
                wx, wy = px + 150, py - 150

        self.wolf = WeakWolf(wx, wy)
        self._show_message("Волк! Подберите оружие поблизости.", 4.0)

    def _pickup_loots(self):
        if not self.loots:
            return
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.size, self.player.size)

        weapon_loots = [l for l in self.loots if l.item_id in ("pistol", "magazine")]
        for loot in weapon_loots:
            loot_rect = pygame.Rect(loot.x, loot.y, loot.size, loot.size)
            if not player_rect.colliderect(loot_rect):
                continue
            if any(l.item_id == "pistol" for l in weapon_loots):
                self.player.obtain_pistol()
                self.player.add_item("magazine", 3)
                self.weapon_picked_up = True
                self._show_message("Зажать ЛКМ для выстрела", 5.0)
            for l in weapon_loots:
                if l in self.loots:
                    self.loots.remove(l)
            break

        for loot in self.loots[:]:
            if loot.item_id in ("pistol", "magazine"):
                continue
            loot_rect = pygame.Rect(loot.x, loot.y, loot.size, loot.size)
            if player_rect.colliderect(loot_rect):
                self.player.add_item(loot.item_id, 1)
                self.loots.remove(loot)

    def _on_inventory_closed(self):
        if self.wolf_killed and not self.show_footprints:
            self.show_footprints = True
            self.wakeup_sub = "follow_tracks"

    def _update_footprint_progress(self):
        if not self.show_footprints or not self.footprints:
            return
        px = self.player.x + self.player.size // 2
        py = self.player.y + self.player.size // 2
        while self.footprint_trigger_index < len(self.footprints):
            fx, fy = self.footprints[self.footprint_trigger_index]
            if math.hypot(px - fx, py - fy) < 35:
                self.footprint_trigger_index += 1
            else:
                break
        self._check_exit_fade()

    def _check_exit_fade(self):
        if self.wakeup_sub == "fade":
            return
        ex, ey = self.exit_point
        px = self.player.x + self.player.size // 2
        py = self.player.y + self.player.size // 2
        if math.hypot(px - ex, py - ey) < 70:
            self.wakeup_sub = "fade"
            self.fade_out_alpha = 0

    def handle_event(self, event):
        if self.phase not in ("wakeup", "revisit"):
            return self
        if self.phase == "revisit":
            return self

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                return _PrologueInventory(self.player, self)
            if event.key == pygame.K_r:
                if self.player.active_item_id == "pistol":
                    pistol_stack = self.player.get_stack("pistol")
                    if pistol_stack and pistol_stack.durability == 0:
                        if self.player.count_item("magazine") > 0:
                            self.player.remove_item("magazine", 1)
                            pistol_stack.durability = 8
            for i, key in enumerate([pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5]):
                if event.key == key:
                    self.player.use_hotbar_item(i)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.player.active_item_id == "pistol" or self.player.has_item("pistol"):
                if self.player.active_item_id != "pistol":
                    self.player.add_to_hotbar("pistol")
                mouse_pos = pygame.mouse.get_pos()
                enemies = [self.wolf] if self.wolf and not self.wolf.dying else []
                perform_attack(self.player, enemies, mouse_pos,
                               self._camera, self.projectiles)

        return self

    def update(self):
        dt = 1 / 60
        self.timer += dt

        if self.phase == "helicopter":
            self.heli_timer += dt

            if self.heli_phase == "center":
                self.heli_x = WIDTH // 2 + math.sin(self.heli_timer * 2) * 5
                self.heli_y = HEIGHT // 3 + math.cos(self.heli_timer * 1.5) * 3
                if self.heli_timer >= self.center_duration:
                    self.heli_phase = "descend"
                    self.heli_timer = 0
                    self.descend_start_x = self.heli_x
                    self.descend_start_y = self.heli_y
                    self.smoke_particles.clear()

            elif self.heli_phase == "descend":
                t = min(self.heli_timer / self.descend_duration, 1.0)
                self.heli_x = self.descend_start_x + (self.descend_target_x - self.descend_start_x) * t
                self.heli_y = self.descend_start_y + (self.descend_target_y - self.descend_start_y) * t
                self._update_smoke(dt)
                if t >= 1.0:
                    self.phase = "crash"
                    self.timer = 0
                    self.crash_alpha = 0
                    if self.helicopter_channel:
                        self.helicopter_channel.stop()

            self._update_dialogues()

        elif self.phase == "crash":
            self.crash_alpha = min(255, self.crash_alpha + 3)
            if self.timer > 2.0:
                self.phase = "blackout"
                self.timer = 0

        elif self.phase == "blackout":
            if self.timer > 2.5:
                self.phase = "wakeup"
                self.timer = 0
                self.player.x, self.player.y = self.spawn_point
                self.loots = []
                self._generate_wreckage()
                self._generate_footprints()
                self._spawn_weapon_loot()
                self._spawn_food_loot()
                self.wolf_spawn_timer = 0.0

        elif self.phase == "wakeup":
            keys = pygame.key.get_pressed()
            obstacles = self.tree_obstacles + self.wreckages
            self.player.move(keys, obstacles)
            self.player.update()

            if self.message_timer > 0:
                self.message_timer -= dt
                if self.message_timer <= 0:
                    self.message = None

            self._pickup_loots()

            if not self.wolf and not self.wolf_killed:
                self.wolf_spawn_timer += dt
                if self.wolf_spawn_timer >= self.wolf_spawn_delay:
                    self._spawn_wolf()

            if self.wolf:
                should_remove = self.wolf.update(
                    self.player, [self.wolf], obstacles, environment=None
                )
                if should_remove:
                    self.wolf = None
                    self.wolf_killed = True
                    self.wakeup_sub = "post_kill"
                    self._show_message("Нажмите I — открыть инвентарь", 6.0)
                elif self.wolf.dying and self.wolf.death_timer <= 50 and not self.wolf_killed:
                    self.wolf_killed = True
                    self.wakeup_sub = "post_kill"
                    self._show_message("Нажмите I — открыть инвентарь", 6.0)

            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0] and self.shoot_cooldown <= 0 and self.wolf and not self.wolf.dying:
                if self.player.has_item("pistol"):
                    if self.player.active_item_id != "pistol":
                        self.player.add_to_hotbar("pistol")
                    mouse_pos = pygame.mouse.get_pos()
                    if perform_attack(self.player, [self.wolf], mouse_pos,
                                      self._camera, self.projectiles):
                        self.shoot_cooldown = 12

            for proj in self.projectiles[:]:
                proj.update([self.wolf] if self.wolf else [], obstacles)
                if not proj.active:
                    self.projectiles.remove(proj)

            if self.show_footprints:
                self._update_footprint_progress()

            if self.wakeup_sub == "fade":
                self.fade_out_alpha = min(255, self.fade_out_alpha + 2)
                if self.fade_out_alpha >= 255:
                    self.phase = "done"

            if not self.player.alive:
                self.phase = "done"

            for wreck in self.wreckages:
                wreck.update()

        elif self.phase == "revisit":
            keys = pygame.key.get_pressed()
            obstacles = self.tree_obstacles + self.wreckages
            self.player.move(keys, obstacles)
            self.player.update()
            for wreck in self.wreckages:
                wreck.update()
            if self.game_scene and self.player.x + self.player.size >= WIDTH - 30:
                crash_x, crash_y = self.world_environment.get_crash_site_world_pos()
                self.game_scene.player.__dict__.update(self.player.__dict__)
                self.game_scene.player.x = crash_x + CRASH_SITE_RADIUS + 40
                self.game_scene.player.y = crash_y
                return self.game_scene
            return self

        elif self.phase == "done":
            from game.scenes.game_scene import GameScene
            spawn_x, spawn_y = self.world_environment.get_game_spawn_after_prologue()
            self.player.x = spawn_x
            self.player.y = spawn_y
            return GameScene(data={
                "player": self.player.__dict__,
                "tutorial_completed": True,
                "prologue_completed": True,
                "spawn_x": spawn_x,
                "spawn_y": spawn_y,
            })

        return self

    def _update_smoke(self, dt):
        if random.random() < 0.3:
            smoke_x = self.heli_x - 50 + random.randint(-5, 5)
            smoke_y = self.heli_y + 5 + random.randint(-5, 5)
            self.smoke_particles.append([smoke_x, smoke_y, 255, random.randint(4, 8)])
        for p in self.smoke_particles[:]:
            p[1] -= 0.5
            p[2] = max(0, p[2] - 2)
            p[3] += 0.05
            if p[2] <= 0:
                self.smoke_particles.remove(p)

    def _update_dialogues(self):
        if self.current_dialogue_index < len(self.dialogues):
            next_dialogue = self.dialogues[self.current_dialogue_index]
            if self.timer >= next_dialogue["time"]:
                self.current_dialogue = next_dialogue
                self.dialogue_active = True
                self.dialogue_timer = 0
                self.current_dialogue_index += 1
        if self.dialogue_active:
            self.dialogue_timer += 1 / 60
            if self.dialogue_timer >= self.dialogue_duration:
                self.dialogue_active = False

    def _generate_footprints(self):
        self.footprints.clear()
        sx, sy = self.spawn_point
        end_x = WIDTH - 15
        end_y = HEIGHT // 2 + random.randint(-25, 25)
        self.exit_point = (end_x, end_y)
        steps = 24
        for i in range(steps):
            t = i / (steps - 1)
            x = sx + (end_x - sx) * t + random.randint(-4, 4)
            y = sy + (end_y - sy) * t + random.randint(-4, 4)
            for _ in range(10):
                hit = False
                for obs in self.tree_obstacles + self.wreckages:
                    if obs.rect.collidepoint(x, y):
                        x += 15
                        hit = True
                        break
                if not hit:
                    break
            self.footprints.append((x, y))
        self.footprint_index = 0
        self.footprint_trigger_index = 0

    def _generate_trees(self):
        self.trees.clear()
        self.tree_obstacles.clear()
        safe_radius = 200
        spawn_x, spawn_y = self.spawn_point

        for _ in range(20):
            for attempt in range(50):
                tx = random.randint(100, WIDTH - 50)
                ty = random.randint(80, HEIGHT - 120)
                world_x = tx + self.world_offset_x
                world_y = ty + self.world_offset_y
                if self.environment.get_tile(world_x, world_y) != 'grass':
                    continue
                if math.hypot(tx - spawn_x, ty - spawn_y) < safe_radius:
                    continue
                too_close = False
                for (ox, oy) in self.trees:
                    if math.hypot(tx - ox, ty - oy) < 45:
                        too_close = True
                        break
                if not too_close:
                    self.trees.append((tx, ty))
                    rect = pygame.Rect(tx - 4, ty - 15, 8, 20)
                    self.tree_obstacles.append(WreckagePiece(rect))
                    break

    def _generate_static_wreckage(self):
        """Негорящие обломки для revisit-сцены."""
        self.wreckages.clear()
        safe_rect = pygame.Rect(self.spawn_point[0], self.spawn_point[1], 40, 40)
        target_count = random.randint(12, 16)
        attempts = 0
        while len(self.wreckages) < target_count and attempts < 200:
            x = random.randint(80, WIDTH - 60)
            y = random.randint(120, HEIGHT - 80)
            if safe_rect.colliderect(pygame.Rect(x, y, 25, 20)):
                attempts += 1
                continue
            if self._screen_tile(x, y) == 'water':
                attempts += 1
                continue
            overlap = False
            new_rect = pygame.Rect(x, y, 25, 20)
            for wr in self.wreckages:
                if wr.rect.colliderect(new_rect):
                    overlap = True
                    break
            if not overlap:
                self.wreckages.append(StaticWreckage(x, y))
            attempts += 1

    def _generate_wreckage(self):
        self.wreckages.clear()
        safe_rect = pygame.Rect(self.spawn_point[0], self.spawn_point[1], 10, 10)
        attempts = 0
        max_attempts = 300
        target_count = random.randint(40, 45)
        while len(self.wreckages) < target_count and attempts < max_attempts:
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 50)
            w = random.randint(15, 50)
            h = random.randint(10, 30)
            new_rect = pygame.Rect(x, y, w, h)
            if safe_rect.colliderect(new_rect):
                attempts += 1
                continue
            overlap = False
            for wr in self.wreckages:
                if wr.rect.colliderect(new_rect):
                    intersect = wr.rect.clip(new_rect)
                    area = intersect.width * intersect.height
                    if area > 0.3 * (wr.rect.width * wr.rect.height):
                        overlap = True
                        break
            if not overlap:
                self.wreckages.append(HelicopterWreckage(x, y))
            attempts += 1

    def _draw_message(self, screen):
        if not self.message:
            return
        text = self.small_font.render(self.message, True, WHITE)
        pad = 12
        box_w = text.get_width() + pad * 2
        box_h = text.get_height() + pad * 2
        box_x = WIDTH // 2 - box_w // 2
        box_y = HEIGHT - 90
        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))
        screen.blit(bg, (box_x, box_y))
        screen.blit(text, (box_x + pad, box_y + pad))

    def draw(self, screen):

        if self.phase == "helicopter":
            screen.fill((135, 206, 235))  # небо

            # Дым (оставляем как есть)
            for p in self.smoke_particles:
                alpha = max(0, int(p[2]))
                if alpha > 0:
                    smoke_surf = pygame.Surface((int(p[3] * 2), int(p[3] * 2)), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surf, (180, 180, 180, alpha), (int(p[3]), int(p[3])), int(p[3]))
                    screen.blit(smoke_surf, (p[0] - p[3], p[1] - p[3]))

            # Загружаем спрайт вертолёта (если ещё не загружен)
            if self.helicopter_sprite is None:
                # Подберите размер под свой спрайт (например, 120×50)
                self.helicopter_sprite = get_sprite('helicopter', (480, 300))

            # Рисуем вертолёт спрайтом
            if self.helicopter_sprite:
                # Центрируем спрайт по координатам heli_x, heli_y
                w, h = self.helicopter_sprite.get_size()
                screen.blit(self.helicopter_sprite, (self.heli_x - w // 2, self.heli_y - h // 2))
            else:
                # Если спрайт не загрузился – рисуем старую "сковородку" как запасной вариант
                cx, cy = self.heli_x, self.heli_y
                pygame.draw.ellipse(screen, (80, 80, 80), (cx - 40, cy - 15, 80, 30))
                pygame.draw.rect(screen, (60, 60, 60), (cx - 60, cy - 8, 30, 10))
                pygame.draw.line(screen, BLACK, (cx, cy - 20), (cx + 25, cy - 5), 3)
                pygame.draw.line(screen, BLACK, (cx, cy - 20), (cx - 25, cy - 5), 3)

            # Диалоги (оставляем как есть)
            if self.dialogue_active and hasattr(self, 'current_dialogue'):
                d = self.current_dialogue
                bar = pygame.Surface((WIDTH, 80), pygame.SRCALPHA)
                bar.fill((0, 0, 0, 150))
                screen.blit(bar, (0, HEIGHT - 80))
                author = self.font.render(d["author"] + ":", True, (255, 200, 100))
                screen.blit(author, (20, HEIGHT - 70))
                words = self.font.render(d["text"], True, WHITE)
                screen.blit(words, (20 + author.get_width() + 10, HEIGHT - 70))

        elif self.phase == "crash":
            screen.fill((135, 206, 235))
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, self.crash_alpha))
            screen.blit(dark, (0, 0))

        elif self.phase == "blackout":
            screen.fill(BLACK)

        elif self.phase in ("wakeup", "done", "revisit"):
            TILE_SIZE = 40
            for y in range(0, HEIGHT, TILE_SIZE):
                for x in range(0, WIDTH, TILE_SIZE):
                    wx = x + self.world_offset_x + TILE_SIZE // 2
                    wy = y + self.world_offset_y + TILE_SIZE // 2
                    tile_type = self.environment.get_tile(wx, wy)
                    if tile_type == 'water':
                        color = (0, 0, 180)
                    elif tile_type == 'sand':
                        color = (194, 178, 128)
                    else:
                        color = (34, 139, 34)
                    pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

            for (tx, ty) in self.trees:
                trunk_rect = pygame.Rect(tx - 4, ty - 15, 8, 20)
                pygame.draw.rect(screen, (101, 67, 33), trunk_rect)
                pygame.draw.circle(screen, (0, 100, 0), (tx, ty - 20), 15)

            for wreck in self.wreckages:
                wreck.draw(screen, 0, 0)

            if self.phase != "revisit":
                for loot in self.loots:
                    loot.draw(screen, 0, 0)

            if self.show_footprints and self.phase != "revisit":
                for i, fp in enumerate(self.footprints):
                    if i < self.footprint_trigger_index:
                        color = (120, 120, 120)
                    else:
                        color = WHITE
                    pygame.draw.circle(screen, color, (int(fp[0]), int(fp[1])), 4)

            if self.phase != "revisit":
                if self.wolf:
                    self.wolf.draw(screen, 0, 0)
                for proj in self.projectiles:
                    proj.draw(screen, 0, 0)

            self.player.draw(screen)

            if self.phase != "revisit":
                self._draw_message(screen)
                if self.wolf_killed and not self.show_footprints:
                    hint = self.small_font.render("Нажмите I — открыть инвентарь", True, (255, 220, 150))
                    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 20))
                elif self.show_footprints and self.wakeup_sub != "fade":
                    hint = self.small_font.render("Следуйте по следам к краю экрана →", True, (200, 200, 255))
                    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 20))
            elif self.game_scene:
                hint = self.small_font.render("Идите вправо, чтобы вернуться на остров →", True, (200, 200, 200))
                screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 20))

            if self.fade_out_alpha > 0:
                dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dark.fill((0, 0, 0, self.fade_out_alpha))
                screen.blit(dark, (0, 0))
