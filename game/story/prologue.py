import pygame
import math
import random
from game.settings import WIDTH, HEIGHT, WORLD_WIDTH, WORLD_HEIGHT, BLACK, WHITE
from game.entities.player import Player
from game.systems.environment import WorldEnvironment
from game.story.helicopter import HelicopterWreckage

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
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 22)

        # Фазы
        self.phase = "helicopter"          # helicopter / crash / blackout / wakeup / done
        self.timer = 0

        # --- Вертолёт ---
        self.heli_x = WIDTH // 2
        self.heli_y = HEIGHT // 3
        self.heli_phase = "center"         # center / descend
        self.heli_timer = 0
        self.center_duration = 0.1         # временно для отладки
        self.descend_duration = 0.1

        self.descend_start_x = self.heli_x
        self.descend_start_y = self.heli_y
        self.descend_target_x = WIDTH + 200
        self.descend_target_y = HEIGHT + 200

        self.tree_obstacles = []           # препятствия деревьев
        self.crash_alpha = 0

        # --- Дым ---
        self.smoke_particles = []

        # --- Диалоги ---
        self.dialogues = [
            {"time": 4.0, "author": "Пилот", "text": "Далеко ещё до этого острова..."},
            {"time": 9.0, "author": "Капитан", "text": "Скоро. По карте уже близко."},
            {"time": 14.5, "author": "Мы", "text": "Я так до конца и не понял, что именно нам там нужно?"},
            {"time": 20.5, "author": "Капитан", "text": "Там есть кое-что важное для корпорации. Доверься мне."},
            {"time": 25.5, "author": "Пилот", "text": "Осторожно! Что-то с двигателем."},
            {"time": 28.0, "author": "Пилот", "text": "Теряю управление! Держитесь!!!"},
        ]
        self.current_dialogue_index = 0
        self.dialogue_active = False
        self.dialogue_timer = 0
        self.dialogue_duration = 0.005

        # --- Игрок и остров ---
        self.player = Player()
        self.environment = WorldEnvironment(WORLD_WIDTH, WORLD_HEIGHT)
        # Смещение, чтобы показать левый край острова
        self.world_offset_x = -150
        self.world_offset_y = 0
        # Точка появления на песке (экранные координаты)
        self.spawn_point = (240, 480)

        # --- Следы ---
        self.footprints = []
        self.footprint_index = 0
        self.show_footprints = False

        # --- Деревья (декорации) ---
        self.trees = []
        self._generate_trees()

        # --- Затемнение при входе в лес ---
        self.fade_out_alpha = 0
        self.wreckages = []

    # --------------------------------------------------------------
    def handle_event(self, event):
        return self

    def update(self):
        dt = 1/60
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
                self._generate_footprints()
                self.show_footprints = True
                self._generate_wreckage()

        elif self.phase == "wakeup":
            keys = pygame.key.get_pressed()
            obstacles = self.tree_obstacles + self.wreckages
            self.player.move(keys, obstacles)
            self.player.update()

            if self.player.x > 600 and self.fade_out_alpha < 255:
                self.fade_out_alpha += 2
                if self.fade_out_alpha >= 255:
                    self.fade_out_alpha = 255
                    self.phase = "done"
            for wreck in self.wreckages:
                wreck.update()

        elif self.phase == "done":
            from game.scenes.game_scene import GameScene
            return GameScene(data={"player": self.player.__dict__})

        return self

    # ---------- вспомогательные методы ----------
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
            self.dialogue_timer += 1/60
            if self.dialogue_timer >= self.dialogue_duration:
                self.dialogue_active = False

    def _generate_footprints(self):
        self.footprints.clear()
        sx, sy = self.spawn_point
        end_x = WIDTH + 80
        end_y = HEIGHT // 2 + 20
        steps = 20
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

    def _generate_trees(self):
        self.trees.clear()
        self.tree_obstacles.clear()
        safe_radius = 200
        spawn_x, spawn_y = self.spawn_point

        for _ in range(30):
            for attempt in range(50):
                tx = random.randint(100, WIDTH - 50)
                ty = random.randint(80, HEIGHT - 120)
                # Проверка, что дерево на траве в мировых координатах
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

    def _generate_wreckage(self):
        self.wreckages.clear()
        # Минимальная безопасная зона вокруг игрока (прямоугольник чуть больше размера игрока)
        safe_rect = pygame.Rect(self.spawn_point[0] , self.spawn_point[1] , 10, 10)
        attempts = 0
        max_attempts = 300
        # Увеличиваем количество обломков
        target_count = random.randint(40, 45)
        while len(self.wreckages) < target_count and attempts < max_attempts:
            x = random.randint(0, WIDTH - 50)
            y = random.randint(0, HEIGHT - 50)
            w = random.randint(15, 50)
            h = random.randint(10, 30)
            new_rect = pygame.Rect(x, y, w, h)
            # Не залезаем только на самую точку спавна игрока
            if safe_rect.colliderect(new_rect):
                attempts += 1
                continue
            # Разрешаем небольшое наложение с другими обломками для плотности
            overlap = False
            for wr in self.wreckages:
                if wr.rect.colliderect(new_rect):
                    # Вычисляем процент пересечения
                    intersect = wr.rect.clip(new_rect)
                    area = intersect.width * intersect.height
                    if area > 0.3 * (wr.rect.width * wr.rect.height):
                        overlap = True
                        break
            if not overlap:
                self.wreckages.append(HelicopterWreckage(x, y))
            attempts += 1

    def draw(self, screen):
        if self.phase == "helicopter":
            screen.fill((135, 206, 235))
            for p in self.smoke_particles:
                alpha = max(0, int(p[2]))
                if alpha > 0:
                    smoke_surf = pygame.Surface((int(p[3]*2), int(p[3]*2)), pygame.SRCALPHA)
                    pygame.draw.circle(smoke_surf, (180, 180, 180, alpha), (int(p[3]), int(p[3])), int(p[3]))
                    screen.blit(smoke_surf, (p[0]-p[3], p[1]-p[3]))
            cx, cy = self.heli_x, self.heli_y
            pygame.draw.ellipse(screen, (80, 80, 80), (cx - 40, cy - 15, 80, 30))
            pygame.draw.rect(screen, (60, 60, 60), (cx - 60, cy - 8, 30, 10))
            pygame.draw.line(screen, BLACK, (cx, cy - 20), (cx + 25, cy - 5), 3)
            pygame.draw.line(screen, BLACK, (cx, cy - 20), (cx - 25, cy - 5), 3)
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

        elif self.phase in ("wakeup", "done"):
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

            if self.show_footprints:
                for fp in self.footprints:
                    pygame.draw.circle(screen, WHITE, (int(fp[0]), int(fp[1])), 4)

            self.player.draw(screen)

            if self.fade_out_alpha > 0:
                dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dark.fill((0, 0, 0, self.fade_out_alpha))
                screen.blit(dark, (0, 0))