import math
import random
import pygame
from game.entities.survivor import Survivor
from game.entities.wolf import StoryWolf


DIALOG_LINES = [
    ("Пилот", "Спасибо, ты вовремя! Я думал, мне конец…"),
    ("Игрок", "Всё в порядке? Мы должны найти капитана."),
    ("Пилот", "Извини, я ранен — не могу идти. Я его видел, он пошёл в нижнюю часть острова."),
    ("Игрок", "Останься пока здесь, я его разыщу и вернусь."),
]


class PilotRescueEpisode:
    PHASE_TRACKS = "tracks"
    PHASE_COMBAT = "combat"
    PHASE_TALK = "talk"
    PHASE_DONE = "done"

    TRIGGER_RADIUS = 300
    INTERACT_RADIUS = 55
    FOOTPRINT_SPACING = 44

    def __init__(self, environment, spawn_x, spawn_y):
        self.environment = environment
        self.phase = self.PHASE_TRACKS
        self.completed = False

        self.encounter_x, self.encounter_y = self._find_encounter_site(spawn_x, spawn_y)
        self.footprints = self._generate_footprints(spawn_x, spawn_y)
        self.footprint_index = 0
        self.combat_activated = False

        self.pilot = Survivor(
            self.encounter_x - 8,
            self.encounter_y - 8,
            survivor_type="pilot",
            name="Пилот",
        )
        self.pilot.found = True
        self.pilot.story_npc = True

        self.wolves = []
        for i in range(4):
            angle = (i / 4) * 2 * math.pi + random.uniform(-0.3, 0.3)
            dist = random.uniform(70, 110)
            wx = self.encounter_x + math.cos(angle) * dist
            wy = self.encounter_y + math.sin(angle) * dist
            wolf = StoryWolf(wx, wy)
            wolf.episode_survivor = self.pilot
            self.wolves.append(wolf)

        self.dialog_active = False
        self.dialog_index = 0
        self.font = pygame.font.SysFont(None, 26)
        self.small_font = pygame.font.SysFont(None, 22)

        

    def _find_encounter_site(self, sx, sy):
        for dist in range(480, 1100, 40):
            for angle_deg in (5, 15, 25, 35, -5, 45):
                rad = math.radians(angle_deg)
                ex = sx + dist * math.cos(rad)
                ey = sy + dist * math.sin(rad)
                if self.environment.get_tile(ex, ey) == "grass":
                    return ex, ey
        return sx + 650, sy + 150

    def _generate_footprints(self, sx, sy):
        points = []
        ex, ey = self.encounter_x, self.encounter_y
        spacing = self.FOOTPRINT_SPACING
        total_len = math.hypot(ex - sx, ey - sy)
        count = max(int(total_len / spacing), 35)

        for i in range(count + 1):
            t = i / count
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            if self.environment.get_tile(x, y) == "water":
                continue
            if points:
                lx, ly = points[-1]
                if math.hypot(x - lx, y - ly) < spacing * 0.9:
                    continue
            points.append((x, y))
        return points

    def _player_center(self, player):
        return player.x + player.size // 2, player.y + player.size // 2

    def _update_footprint_progress(self, player):
        px, py = self._player_center(player)
        while self.footprint_index < len(self.footprints):
            fx, fy = self.footprints[self.footprint_index]
            if math.hypot(px - fx, py - fy) < self.FOOTPRINT_SPACING * 0.85:
                self.footprint_index += 1
            else:
                break

    def _activate_combat(self):
        if self.phase != self.PHASE_TRACKS:
            return
        self.phase = self.PHASE_COMBAT
        self.combat_activated = True
        for wolf in self.wolves:
            wolf.episode_active = True
            wolf.state = "chase"
            wolf.target = self.pilot

    def on_player_shot(self):
        if self.phase != self.PHASE_COMBAT:
            return
        self._aggro_all_to_player()

    def on_wolf_hit(self):
        if self.phase != self.PHASE_COMBAT:
            return
        self._aggro_all_to_player()

    def _aggro_all_to_player(self):
        for wolf in self.wolves:
            wolf.episode_active = True
            wolf.aggro_player = True
            wolf.target = None

    def all_wolves_defeated(self):
        return self.combat_activated and len(self.wolves) == 0

    def living_wolves(self):
        return [w for w in self.wolves if not w.dying and w.health > 0]

    def update(self, player, structures, environment):
        if self.completed:
            return

        px, py = self._player_center(player)

        if self.phase == self.PHASE_TRACKS:
            self._update_footprint_progress(player)
            if math.hypot(px - self.encounter_x, py - self.encounter_y) < self.TRIGGER_RADIUS:
                self._activate_combat()

        elif self.phase == self.PHASE_COMBAT:
            self.pilot.update()
            obstacles = structures
            for wolf in self.wolves[:]:
                should_remove = wolf.update(player, self.wolves, obstacles, environment)
                if should_remove:
                    self.wolves.remove(wolf)
            if self.all_wolves_defeated():
                self.phase = self.PHASE_TALK

        elif self.phase == self.PHASE_TALK:
            self.pilot.update()

        elif self.phase == self.PHASE_DONE:
            self.pilot.update()

    def try_start_dialog(self, player):
        if self.phase != self.PHASE_TALK or self.dialog_active:
            return False
        px, py = self._player_center(player)
        dist = math.hypot(px - (self.pilot.x + self.pilot.size // 2),
                          py - (self.pilot.y + self.pilot.size // 2))
        if dist > self.INTERACT_RADIUS:
            return False
        self.dialog_active = True
        self.dialog_index = 0
        return True

    def advance_dialog(self):
        if not self.dialog_active:
            return
        self.dialog_index += 1
        if self.dialog_index >= len(DIALOG_LINES):
            self.dialog_active = False
            self.phase = self.PHASE_DONE
            self.completed = True
            self.pilot.dialogue_completed = True
            return True
        return False

    def handle_event(self, event):
        if not self.dialog_active:
            return False
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
            self.advance_dialog()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.advance_dialog()
            return True
        return False

    def draw_footprints(self, surface, camera):
        if self.phase != self.PHASE_TRACKS:
            return
        for i, (fx, fy) in enumerate(self.footprints):
            color = (120, 120, 120) if i < self.footprint_index else (255, 255, 255)
            sx, sy = camera.world_to_screen(fx, fy)
            pygame.draw.circle(surface, color, (sx, sy), 4)

    def draw_hint(self, screen):
        if self.completed or self.dialog_active:
            return
        if self.phase == self.PHASE_TRACKS:
            text = "Идите по следам"
        elif self.phase == self.PHASE_COMBAT:
            text = "Защитите пилота — стреляйте в волков (ЛКМ)"
        elif self.phase == self.PHASE_TALK:
            text = "Подойдите к пилоту и нажмите E"
        else:
            return
        surf = self.small_font.render(text, True, (255, 255, 200))
        screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, 12))

    def draw_dialog(self, screen):
        if not self.dialog_active:
            return

        author, text = DIALOG_LINES[self.dialog_index]

        # Размеры диалогового окна (можно настроить под свой вкус)
        bar_width = int(screen.get_width() * 0.9)  # 80% ширины экрана
        bar_height = 140
        bar_x = (screen.get_width() - bar_width) // 2
        bar_y = (screen.get_height() - bar_height) // 2

        # Создаём полупрозрачный фон
        bar = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 200))  # чёрный с прозрачностью
        screen.blit(bar, (bar_x, bar_y))

        # Рамка (опционально)
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)

        # Отрисовка имени автора (центрируем по горизонтали)
        author_color = (255, 200, 100) if author != "Игрок" else (180, 220, 255)
        author_surf = self.font.render(author + ":", True, author_color)
        author_rect = author_surf.get_rect(center=(screen.get_width() // 2, bar_y + 30))
        screen.blit(author_surf, author_rect)

        # Отрисовка текста реплики (центрируем по горизонтали)
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(screen.get_width() // 2, bar_y + 70))
        screen.blit(text_surf, text_rect)

        # Подсказка о продолжении (в правом нижнем углу окна)
        hint = self.small_font.render("E / Пробел — далее", True, (180, 180, 180))
        hint_rect = hint.get_rect(bottomright=(bar_x + bar_width - 10, bar_y + bar_height - 10))
        screen.blit(hint, hint_rect)

    def get_draw_survivors(self):
        return [self.pilot]

    def get_combat_wolves(self):
        if self.phase in (self.PHASE_COMBAT, self.PHASE_TALK, self.PHASE_DONE):
            return self.wolves
        return []

    @classmethod
    def from_completed(cls, environment):
        """Восстанавливает пилота после завершённого эпизода (загрузка сохранения)."""
        ep = cls.__new__(cls)
        ep.environment = environment
        ep.completed = True
        ep.phase = cls.PHASE_DONE
        ep.wolves = []
        ep.footprints = []
        ep.footprint_index = 0
        ep.combat_activated = True
        ep.dialog_active = False
        ep.dialog_index = 0
        ep.font = pygame.font.SysFont(None, 26)
        ep.small_font = pygame.font.SysFont(None, 22)
        px, py = environment.get_pilot_rest_position()
        ep.encounter_x, ep.encounter_y = px, py
        ep.pilot = Survivor(px - 8, py - 8, survivor_type="pilot", name="Пилот")
        ep.pilot.found = True
        ep.pilot.story_npc = True
        ep.pilot.dialogue_completed = True
        return ep
