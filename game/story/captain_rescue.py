import math
import random
import pygame
from game.entities.survivor import Survivor
from game.entities.bear import StoryBear
from game.story.dialogue import draw_dialog_box


CAPTAIN_DIALOG = [
    ("Капитан", "Спасибо, что спас!"),
    ("Игрок", "Ты не ранен? Можешь идти?"),
    ("Капитан", "Всё в порядке."),
    ("Игрок", "Нам надо идти к пилоту и думать, как будем выбираться."),
]

REUNION_DIALOG = [
    ("Пилот", "Ты жив!"),
    ("Капитан", "Так точно."),
    ("Пилот", "Можно построить плот и уплыть отсюда, но понадобится много ресурсов."),
    ("Игрок", "Я займусь этим, а вы пока отдыхайте."),
]


class CaptainRescueEpisode:
    PHASE_SCENE = "scene"
    PHASE_COMBAT = "combat"
    PHASE_CLIMB = "climb"
    PHASE_CAPTAIN_TALK = "captain_talk"
    PHASE_MARCH = "march"
    PHASE_REUNION = "reunion"
    PHASE_DONE = "done"

    COMBAT_TRIGGER_RADIUS = 420
    INTERACT_RADIUS = 55
    BEAR_SIZE = 35

    def __init__(self, environment, pilot):
        self.environment = environment
        self.pilot = pilot
        self.completed = False
        self.phase = self.PHASE_SCENE
        self.combat_activated = False

        px = pilot.x + pilot.size // 2
        py = pilot.y + pilot.size // 2
        site = environment.get_captain_rescue_site(px, py)
        self.shore_x = site["shore_x"]
        self.shore_y = site["shore_y"]
        self.water_x = site["water_x"]
        self.water_y = site["water_y"]

        self.captain = Survivor(
            self.water_x - 8, self.water_y - 8,
            survivor_type="captain", name="Капитан",
        )
        self.captain.found = True
        self.captain.story_npc = True
        self.captain.in_water = True

        self.bears = self._spawn_bears_on_shore()

        self.climb_timer = 0
        self.climb_duration = 90
        self.climb_start = (self.water_x, self.water_y)
        self.climb_end = (self.shore_x - 10, self.shore_y - 10)

        self.dialog_active = False
        self.dialog_lines = []
        self.dialog_kind = None
        self.dialog_index = 0
        self.march_speed = 2.0

        self.font = pygame.font.SysFont(None, 26)
        self.small_font = pygame.font.SysFont(None, 22)
        self.cry_font = pygame.font.SysFont(None, 32)

    def _is_bear_position_valid(self, bx, by):
        size = self.BEAR_SIZE
        points = (
            (bx, by),
            (bx + size, by),
            (bx, by + size),
            (bx + size, by + size),
            (bx + size // 2, by + size // 2),
        )
        return all(
            self.environment.get_tile(px, py) in ("sand", "grass")
            for px, py in points
        )

    def _spawn_bears_on_shore(self):
        target_count = random.randint(2, 4)
        bears = []
        offsets = [
            (-60, -20), (50, -10), (-15, 35), (35, 25),
            (-40, 30), (70, 15), (-80, 10), (20, -35),
        ]
        for ox, oy in offsets:
            if len(bears) >= target_count:
                break
            bx = self.shore_x + ox
            by = self.shore_y + oy
            if not self._is_bear_position_valid(bx, by):
                continue
            if any(math.hypot(bx - b.x, by - b.y) < 45 for b in bears):
                continue
            bears.append(StoryBear(bx, by))

        attempts = 0
        while len(bears) < 2 and attempts < 100:
            attempts += 1
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(35, 130)
            bx = self.shore_x + math.cos(angle) * dist
            by = self.shore_y + math.sin(angle) * dist
            if not self._is_bear_position_valid(bx, by):
                continue
            if any(math.hypot(bx - b.x, by - b.y) < 45 for b in bears):
                continue
            bears.append(StoryBear(bx, by))
        return bears

    def _player_center(self, player):
        return player.x + player.size // 2, player.y + player.size // 2

    def _dist_to_site(self, player):
        px, py = self._player_center(player)
        return math.hypot(px - self.shore_x, py - self.shore_y)

    def _player_in_combat_zone(self, player):
        return self._dist_to_site(player) < self.COMBAT_TRIGGER_RADIUS

    def _activate_combat(self):
        if self.combat_activated:
            return
        self.combat_activated = True
        self.phase = self.PHASE_COMBAT
        for bear in self.bears:
            bear.episode_active = True
            bear.aggro_player = True
            bear.state = "chase"

    def on_player_shot(self, player):
        if self.phase == self.PHASE_SCENE and self._player_in_combat_zone(player):
            self._activate_combat()
        elif self.phase == self.PHASE_COMBAT:
            self._aggro_all_bears()

    def on_player_attack(self, player):
        if self.phase == self.PHASE_SCENE and self._player_in_combat_zone(player):
            self._activate_combat()
        elif self.phase == self.PHASE_COMBAT:
            self._aggro_all_bears()

    def on_bear_hit(self):
        if self.phase == self.PHASE_COMBAT:
            self._aggro_all_bears()

    def _aggro_all_bears(self):
        for bear in self.bears:
            bear.episode_active = True
            bear.aggro_player = True

    def _bears_defeated(self):
        return self.combat_activated and len(self.bears) == 0

    def _move_captain_towards(self, tx, ty, speed):
        dx = tx - self.captain.x
        dy = ty - self.captain.y
        dist = math.hypot(dx, dy)
        if dist <= speed:
            self.captain.x = tx
            self.captain.y = ty
            return True
        self.captain.x += dx / dist * speed
        self.captain.y += dy / dist * speed
        return False

    def update(self, player, structures, environment):
        if self.completed:
            self.captain.update()
            return

        if self.phase == self.PHASE_SCENE:
            self.captain.update()

        elif self.phase == self.PHASE_COMBAT:
            self.captain.update()
            for bear in self.bears[:]:
                should_remove = bear.update(player, self.bears, structures, environment)
                if should_remove:
                    self.bears.remove(bear)
            if self._bears_defeated():
                self.phase = self.PHASE_CLIMB
                self.climb_timer = 0

        elif self.phase == self.PHASE_CLIMB:
            self.climb_timer += 1
            t = min(self.climb_timer / self.climb_duration, 1.0)
            sx, sy = self.climb_start
            ex, ey = self.climb_end
            self.captain.x = sx + (ex - sx) * t
            self.captain.y = sy + (ey - sy) * t
            self.captain.in_water = t < 0.85
            self.captain.update()
            if t >= 1.0:
                self.captain.in_water = False
                self.phase = self.PHASE_CAPTAIN_TALK

        elif self.phase == self.PHASE_CAPTAIN_TALK:
            self.captain.update()

        elif self.phase == self.PHASE_MARCH:
            self.captain.update()
            pilot_x = self.pilot.x + self.pilot.size // 2 - self.captain.size // 2
            pilot_y = self.pilot.y + self.pilot.size // 2 + 20
            if self._move_captain_towards(pilot_x, pilot_y, self.march_speed):
                self.phase = self.PHASE_REUNION
                self.dialog_lines = REUNION_DIALOG
                self.dialog_kind = "reunion"
                self.dialog_active = True
                self.dialog_index = 0

        elif self.phase == self.PHASE_REUNION:
            self.captain.update()

        elif self.phase == self.PHASE_DONE:
            self.captain.update()

    def try_start_captain_dialog(self, player):
        if self.phase != self.PHASE_CAPTAIN_TALK or self.dialog_active:
            return False
        px, py = self._player_center(player)
        cx = self.captain.x + self.captain.size // 2
        cy = self.captain.y + self.captain.size // 2
        if math.hypot(px - cx, py - cy) > self.INTERACT_RADIUS:
            return False
        self.dialog_lines = CAPTAIN_DIALOG
        self.dialog_kind = "captain"
        self.dialog_active = True
        self.dialog_index = 0
        return True

    def advance_dialog(self):
        if not self.dialog_active:
            return
        self.dialog_index += 1
        if self.dialog_index >= len(self.dialog_lines):
            self.dialog_active = False
            if self.dialog_kind == "captain":
                self.phase = self.PHASE_MARCH
            elif self.dialog_kind == "reunion":
                self.phase = self.PHASE_DONE
                self.completed = True
                self.captain.dialogue_completed = True
            self.dialog_kind = None

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

    def draw_bears(self, surface, camera):
        from game.assets.sprites import blit_entity
        for bear in self.bears:
            blit_entity(
                surface, "bear", bear.x, bear.y, bear.size,
                camera.x, camera.y,
                hit=bear.hit_timer > 0,
                dying=bear.dying,
            )

    def draw_hint(self, screen, player, camera=None):
        if self.completed or self.dialog_active:
            return
        dist = self._dist_to_site(player)
        if self.phase == self.PHASE_SCENE:
            if dist > 250:
                text = "Идите на юго-восток — там капитан"
            else:
                cry = self.cry_font.render("Помогите!", True, (255, 120, 120))
                screen.blit(cry, (screen.get_width() // 2 - cry.get_width() // 2, 12))
                return
            surf = self.small_font.render(text, True, (255, 255, 200))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, 12))
        elif self.phase == self.PHASE_COMBAT:
            surf = self.small_font.render("Убейте медведей!", True, (255, 255, 200))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, 12))
        elif self.phase == self.PHASE_CAPTAIN_TALK:
            surf = self.small_font.render("Подойдите к капитану и нажмите E", True, (255, 255, 200))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, 12))
        elif self.phase == self.PHASE_MARCH:
            surf = self.small_font.render("Капитан идёт к пилоту...", True, (200, 220, 255))
            screen.blit(surf, (screen.get_width() // 2 - surf.get_width() // 2, 12))

    def draw_dialog(self, screen):
        if not self.dialog_active:
            return
        author, text = self.dialog_lines[self.dialog_index]
        draw_dialog_box(screen, author, text, self.font, self.small_font)

    def get_draw_survivors(self):
        return [self.captain]

    def get_combat_bears(self):
        if self.phase == self.PHASE_COMBAT:
            return self.bears
        return []

    def get_bears_for_draw(self):
        return self.bears

    def should_render(self, player):
        return True

    @classmethod
    def from_completed(cls, environment, pilot):
        """Капитан у пилота после завершённого эпизода (загрузка сохранения)."""
        ep = cls.__new__(cls)
        ep.environment = environment
        ep.pilot = pilot
        ep.completed = True
        ep.phase = cls.PHASE_DONE
        ep.combat_activated = True
        ep.bears = []
        ep.dialog_active = False
        ep.dialog_index = 0
        ep.dialog_kind = None
        ep.font = pygame.font.SysFont(None, 26)
        ep.small_font = pygame.font.SysFont(None, 22)
        ep.cry_font = pygame.font.SysFont(None, 32)
        ep.march_speed = 2.0
        ep.climb_timer = 0
        ep.climb_duration = 0
        ep.climb_start = (0, 0)
        ep.climb_end = (0, 0)

        site = environment.get_captain_rescue_site(
            pilot.x + pilot.size // 2,
            pilot.y + pilot.size // 2,
        )
        ep.shore_x = site["shore_x"]
        ep.shore_y = site["shore_y"]
        ep.water_x = site["water_x"]
        ep.water_y = site["water_y"]

        captain_x = pilot.x + pilot.size // 2 - 8 + 35
        captain_y = pilot.y + pilot.size // 2 + 12
        ep.captain = Survivor(
            captain_x, captain_y,
            survivor_type="captain", name="Капитан",
        )
        ep.captain.found = True
        ep.captain.story_npc = True
        ep.captain.in_water = False
        ep.captain.dialogue_completed = True
        return ep
