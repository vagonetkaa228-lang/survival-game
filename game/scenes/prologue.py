# game/scenes/prologue.py

import pygame
import math
import random
from game.settings import WIDTH, HEIGHT, BLACK, WHITE, RED, GREEN
from game.entities.player import Player
from game.entities.wolf import Wolf
from game.entities.projectiles import Projectile
from game.items.registry import ITEMS
from game.ui.button import Button

# Добавим временный предмет "тушёнка" для обучения
if "canned_food" not in ITEMS:
    from game.items.consumable import Food

    ITEMS["canned_food"] = Food("canned_food", "Тушёнка", hunger_restore=30, health_restore=10)


class PrologueScene:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 48)
        self.phase = "helicopter"  # helicopter / crash / blackout / wakeup / wolf_fight / tutorial / footprints / done
        self.timer = 0
        self.player = Player()
        # Начальная позиция игрока (будет задана после крушения)
        self.spawn_point = (0, 0)
        self.movement_radius = 150  # пикселей от точки появления
        self.wolf = None
        self.projectiles = []
        self.obstacles = []  # декорации обломков (непроходимые? сделаем проходимыми, просто спрайты)
        self.footprints = []  # точки следов
        self.footprint_index = 0
        self.show_inventory_hint = False
        self.show_use_item_hint = False
        self.tutorial_done = False
        self.heli_angle = 0
        self.crash_shake = 0
        self.crash_alpha = 0

        # Для ограничения движения
        self.allowed_rect = None

        # Заглушка звука (pygame.mixer.Sound можно добавить позже)
        # self.sound_crash = pygame.mixer.Sound("assets/sounds/crash.wav")

    def handle_event(self, event):
        if self.phase == "done":
            from game.scenes.game_scene import GameScene
            # Передаём данные игрока (пистолет, патроны, предметы туториала)
            return GameScene(data={"player": self.player.__dict__})

        if event.type == pygame.KEYDOWN:
            if self.phase == "tutorial":
                if event.key == pygame.K_i:
                    # Открываем инвентарь – этот вызов перехватывается в GameScene, но мы эмулируем
                    self.show_inventory_hint = False
                    self.show_use_item_hint = True
                    # Добавляем в инвентарь тушёнку, если ещё не добавлена
                    if "canned_food" not in self.player.inventory:
                        self.player.add_item("canned_food", 1)
                elif event.key == pygame.K_e and self.show_use_item_hint:
                    # Эмулируем использование предмета (игрок нажал E на тушёнке в инвентаре)
                    # В реальности это произойдёт при клике по слоту в InventoryScene, но здесь проверим
                    if "canned_food" in self.player.inventory:
                        self.player.use_item("canned_food")
                        self.show_use_item_hint = False
                        self.phase = "footprints"
                        self.generate_footprints()
            elif self.phase == "footprints":
                # Можно нажать I для инвентаря, но не обязательно
                pass

        # Обработка выстрела (левая кнопка мыши)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.phase == "wolf_fight" and self.player.active_item_id == "pistol":
                # Упрощённая стрельба: создаём снаряд в направлении мыши
                mouse_x, mouse_y = event.pos
                px = self.player.x + self.player.size // 2
                py = self.player.y + self.player.size // 2
                angle = math.atan2(mouse_y - py, mouse_x - px)
                # Проверим наличие магазина (прочность пистолета > 0)
                stack = self.player.inventory.get("pistol")
                if stack and stack.durability > 0:
                    self.player.consume_tool_durability("pistol")
                    proj = Projectile(px, py, angle, speed=15, damage=15)
                    self.projectiles.append(proj)
                    # Звук выстрела
                    # pygame.mixer.Sound("assets/sounds/gunshot.wav").play()

        return self

    def update(self):
        dt = 1 / 60
        self.timer += dt

        # Анимация вертолёта
        if self.phase == "helicopter":
            self.heli_angle += 0.5
            if self.timer > 3:
                self.phase = "crash"
                self.timer = 0
                self.crash_shake = 10
                # pygame.mixer.Sound.play(self.sound_crash)
        elif self.phase == "crash":
            self.crash_shake = max(0, self.crash_shake - 0.5)
            self.crash_alpha = min(255, self.crash_alpha + 2)
            if self.timer > 2:
                self.phase = "blackout"
                self.timer = 0
        elif self.phase == "blackout":
            if self.timer > 2:
                # Просыпаемся на обломках
                self.phase = "wakeup"
                self.timer = 0
                # Устанавливаем точку появления и позицию игрока
                self.spawn_point = (WIDTH // 2, HEIGHT // 2 + 50)
                self.player.x, self.player.y = self.spawn_point
                self.allowed_rect = pygame.Rect(
                    self.spawn_point[0] - self.movement_radius,
                    self.spawn_point[1] - self.movement_radius,
                    self.movement_radius * 2,
                    self.movement_radius * 2
                )
                # Генерируем декорации обломков (несколько прямоугольников)
                self.obstacles = self.create_wreckage()
                # Даём пистолет и патроны (они лежат рядом, но подберутся автоматически)
                self.player.obtain_pistol()
                self.player.add_item("magazine", 3)
                # Через 5-10 секунд появится волк
                self.wolf_spawn_delay = random.uniform(5, 10)
        elif self.phase == "wakeup":
            self.wolf_spawn_delay -= dt
            # Ограничиваем движение игрока
            self.clamp_player_position()
            if self.wolf_spawn_delay <= 0:
                self.spawn_wolf()
                self.phase = "wolf_fight"
        elif self.phase == "wolf_fight":
            self.clamp_player_position()
            # Обновляем волка
            if self.wolf:
                self.wolf.update(self.player, [], [], None)  # без структур и окружения
                if self.wolf.health <= 0:
                    self.wolf.dying = True  # запускаем таймер смерти
                    self.wolf.health = 0
                    self.phase = "tutorial"
                    self.timer = 0
                    self.show_inventory_hint = True
                    self.wolf = None
            # Обновляем снаряды
            for proj in self.projectiles[:]:
                proj.update([self.wolf] if self.wolf else [], self.obstacles)
                if not proj.active:
                    self.projectiles.remove(proj)
        elif self.phase == "tutorial":
            # Ждём действий игрока
            pass
        elif self.phase == "footprints":
            # Разрешаем свободное движение, но в пределах большой области
            self.clamp_player_position(radius=300)
            # Проверяем, наступил ли игрок на последний след
            if self.footprint_index < len(self.footprints):
                fx, fy = self.footprints[self.footprint_index]
                # Если игрок близко к следующему следу, активируем его и переходим к следующему
                if math.hypot(self.player.x - fx, self.player.y - fy) < 30:
                    self.footprint_index += 1
                    if self.footprint_index >= len(self.footprints):
                        # Дошли до конца следов – завершаем пролог
                        self.phase = "done"
                        self.player.health = 100  # восстанавливаем здоровье после возможных повреждений
        elif self.phase == "done":
            pass

        # Общие обновления игрока
        keys = pygame.key.get_pressed()
        # Движение игрока разрешено во всех фазах, кроме вертолёта и крушения
        if self.phase not in ("helicopter", "crash", "blackout"):
            self.player.move(keys, self.obstacles if self.phase != "wolf_fight" else [])
        self.player.update()

    def clamp_player_position(self, radius=None):
        """Ограничивает позицию игрока заданным радиусом от точки спавна."""
        if radius is None:
            radius = self.movement_radius
        center_x, center_y = self.spawn_point
        dx = self.player.x - center_x
        dy = self.player.y - center_y
        dist = math.hypot(dx, dy)
        if dist > radius:
            self.player.x = center_x + dx / dist * radius
            self.player.y = center_y + dy / dist * radius

    def spawn_wolf(self):
        """Создаёт слабого волка на краю экрана."""
        angle = random.uniform(0, 2 * math.pi)
        dist = 300
        wolf_x = self.player.x + math.cos(angle) * dist
        wolf_y = self.player.y + math.sin(angle) * dist
        self.wolf = Wolf(wolf_x, wolf_y)
        self.wolf.health = 20  # ослабленный
        self.wolf.max_health = 20
        self.wolf.speed = 1.5
        self.wolf.damage = 5  # чтобы не убил игрока сразу

    def create_wreckage(self):
        """Генерирует прямоугольники обломков вокруг точки появления."""
        rects = []
        # Несколько случайных обломков вокруг
        for _ in range(8):
            w = random.randint(20, 60)
            h = random.randint(10, 30)
            x = self.spawn_point[0] + random.randint(-120, 120)
            y = self.spawn_point[1] + random.randint(-120, 120)
            rects.append(pygame.Rect(x, y, w, h))
        return rects

    def generate_footprints(self):
        """Создаёт цепочку следов, ведущую вправо вниз."""
        self.footprints = []
        start_x = self.player.x
        start_y = self.player.y + 40
        for i in range(10):
            x = start_x + i * 25 + random.randint(-5, 5)
            y = start_y + i * 5 + random.randint(-3, 3)
            self.footprints.append((x, y))

    def draw(self, screen):
        if self.phase == "helicopter":
            # Простой вертолёт из примитивов
            screen.fill((135, 206, 235))  # небо
            # Вертолёт
            cx = WIDTH // 2 + math.sin(self.heli_angle) * 5
            cy = HEIGHT // 2 - 50 + math.cos(self.heli_angle * 1.5) * 3
            # Корпус
            pygame.draw.ellipse(screen, (100, 100, 100), (cx - 40, cy - 15, 80, 30))
            # Хвост
            pygame.draw.rect(screen, (80, 80, 80), (cx - 60, cy - 8, 30, 10))
            # Винт
            pygame.draw.line(screen, (0, 0, 0), (cx, cy - 20), (cx + 30, cy - 5), 4)
            pygame.draw.line(screen, (0, 0, 0), (cx, cy - 20), (cx - 30, cy - 5), 4)
            # Текст
            text = self.big_font.render("День 0: Экспедиция", True, BLACK)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 50))

        elif self.phase == "crash":
            screen.fill((135, 206, 235))
            # Рисуем тот же вертолёт, но с тряской
            shake_x = random.randint(-self.crash_shake, self.crash_shake)
            shake_y = random.randint(-self.crash_shake, self.crash_shake)
            # ... (аналогично вертолёту с shake_x, shake_y)
            # Затемнение
            dark = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dark.fill((0, 0, 0, self.crash_alpha))
            screen.blit(dark, (0, 0))

        elif self.phase == "blackout":
            screen.fill(BLACK)
            # Звук падения уже воспроизведён

        elif self.phase in ("wakeup", "wolf_fight", "tutorial", "footprints"):
            # Фон: земля, обломки
            screen.fill((34, 139, 34))  # трава
            # Песок вокруг точки спавна? можно нарисовать эллипс
            pygame.draw.ellipse(screen, (194, 178, 128),
                                (self.spawn_point[0] - 80, self.spawn_point[1] - 80, 160, 160))
            # Обломки
            for rect in self.obstacles:
                pygame.draw.rect(screen, (80, 80, 80), rect)
            # Рисуем игрока
            self.player.draw(screen)
            # Волк
            if self.wolf:
                self.wolf.draw(screen, 0, 0)
            # Снаряды
            for proj in self.projectiles:
                proj.draw(screen, 0, 0)
            # Ограничение движения (невидимая граница) – для отладки можно показать круг
            # pygame.draw.circle(screen, (255,0,0), self.spawn_point, self.movement_radius, 2)

            # Подсказки
            if self.phase == "tutorial":
                if self.show_inventory_hint:
                    text = self.font.render("Нажмите I, чтобы открыть инвентарь", True, WHITE)
                    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 60))
                elif self.show_use_item_hint:
                    text = self.font.render("Нажмите E или кликните по тушёнке в инвентаре", True, WHITE)
                    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT - 60))

            if self.phase == "footprints":
                # Рисуем следы до активированных
                for i, (fx, fy) in enumerate(self.footprints):
                    color = (255, 255, 255) if i < self.footprint_index else (150, 150, 150)
                    pygame.draw.circle(screen, color, (int(fx), int(fy)), 3)
                # Подсказка идти по следам
                if self.footprint_index < len(self.footprints):
                    hint = self.font.render("Идите по следам", True, WHITE)
                    screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 20))

        elif self.phase == "done":
            # Плавный переход в игру (можно затемнение)
            screen.fill(BLACK)
            text = self.big_font.render("Загрузка...", True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))