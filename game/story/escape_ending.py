import math
import pygame
from game.settings import WIDTH, HEIGHT
from game.ui.button import Button


class EscapeEndingScene:
    """Финальная сцена: уплывание на плоту → экран победы."""

    def __init__(self, player, pilot, captain):
        self.player = player
        self.pilot = pilot
        self.captain = captain

        self.phase = "board"
        self.board_timer = 90
        self.raft_x = WIDTH // 2 - 70
        self.raft_y = HEIGHT // 2 + 60
        self.raft_speed = 2.2
        self.fade_alpha = 0
        self.fade_speed = 1.2
        self.wave_time = 0.0

        self.time = 0.0
        self.overlay_alpha = 0
        self.text_alpha = 0

        self.font_big = pygame.font.SysFont(None, 64)
        self.font = pygame.font.SysFont(None, 36)
        center_x = WIDTH // 2
        self.menu_btn = Button(
            "Выйти в меню",
            center_x - 300, 380, 600, 60,
            base_color=(30, 90, 70),
            hover_color=(60, 160, 120),
        )

    def handle_event(self, event):
        if self.phase == "victory":
            if self.menu_btn.clicked(event):
                from game.scenes.menu import MenuScene
                return MenuScene()
        return self

    def update(self):
        self.wave_time += 0.04

        if self.phase == "board":
            self.board_timer -= 1
            if self.board_timer <= 0:
                self.phase = "sail"
        elif self.phase == "sail":
            self.raft_x += self.raft_speed
            self.raft_y -= 0.35
            if self.raft_x > WIDTH + 120:
                self.phase = "fade"
        elif self.phase == "fade":
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            if self.fade_alpha >= 255:
                self.phase = "victory"
                self.fade_alpha = 255
        elif self.phase == "victory":
            self.time += 0.01
            self.overlay_alpha += (140 - self.overlay_alpha) * 0.06
            self.text_alpha += (255 - self.text_alpha) * 0.08
            self.menu_btn.update()

        return None

    def _draw_sail_background(self, screen):
        for y in range(HEIGHT):
            t = y / HEIGHT
            if t < 0.55:
                r = int(40 + 30 * t)
                g = int(90 + 50 * t)
                b = int(140 + 40 * t)
            elif t < 0.72:
                blend = (t - 0.55) / 0.17
                r = int(70 + 120 * blend)
                g = int(130 + 60 * blend)
                b = int(160 - 40 * blend)
            else:
                r = int(190 + 20 * (t - 0.72))
                g = int(170 + 30 * (t - 0.72))
                b = int(110 + 20 * (t - 0.72))
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        beach_y = int(HEIGHT * 0.72)
        for y in range(beach_y, HEIGHT):
            t = (y - beach_y) / max(HEIGHT - beach_y, 1)
            color = (int(210 - 30 * t), int(185 - 25 * t), int(120 - 15 * t))
            pygame.draw.line(screen, color, (0, y), (WIDTH, y))

        for i in range(8):
            wx = (i * 110 + int(self.wave_time * 40)) % (WIDTH + 80) - 40
            wy = int(HEIGHT * 0.68 + 8 * math.sin(self.wave_time + i))
            pygame.draw.arc(
                screen, (60, 110, 160),
                (wx, wy, 90, 18), 0, math.pi, 2,
            )

    def _draw_victory_background(self, screen):
        """Золотисто-бирюзовый фон — отличный от меню и экрана смерти."""
        for y in range(HEIGHT):
            wave = int(10 * math.sin(self.time + y * 0.02))
            t = y / HEIGHT
            if t < 0.35:
                r = min(25 + y // 18 + wave, 55)
                g = min(70 + y // 10 + wave, 110)
                b = min(100 + y // 8 + wave, 150)
            elif t < 0.65:
                blend = (t - 0.35) / 0.3
                r = int(40 + 180 * blend + wave)
                g = int(100 + 120 * blend + wave // 2)
                b = int(140 - 60 * blend)
            else:
                r = min(220 + wave, 255)
                g = min(170 + y // 20 + wave, 220)
                b = min(90 + y // 25, 130)

            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        for i in range(24):
            x = (i * 95 + int(self.time * 45)) % (WIDTH + 60) - 30
            y = (i * 55 + int(self.time * 25)) % (HEIGHT + 40) - 20
            pulse = 0.5 + 0.5 * math.sin(self.time * 2 + i)
            radius = 2 + int(pulse)
            color = (255, 230, 140) if i % 3 == 0 else (180, 230, 255)
            pygame.draw.circle(screen, color, (x, y), radius)

        horizon_y = int(HEIGHT * 0.62)
        for i in range(6):
            wx = (i * 160 + int(self.time * 35)) % (WIDTH + 100) - 50
            wy = horizon_y + int(6 * math.sin(self.time * 1.5 + i))
            pygame.draw.arc(
                screen, (200, 220, 170),
                (wx, wy, 110, 20), 0, math.pi, 2,
            )

    def _draw_raft(self, screen):
        bob = int(3 * math.sin(self.wave_time * 2))
        rx = int(self.raft_x)
        ry = int(self.raft_y + bob)
        raft_w, raft_h = 140, 28

        pygame.draw.rect(screen, (90, 55, 25), (rx, ry + 4, raft_w, raft_h), border_radius=4)
        for i in range(5):
            lx = rx + 8 + i * 26
            pygame.draw.rect(screen, (120, 75, 35), (lx, ry, 22, raft_h + 6), border_radius=3)

        chars = [
            (rx + 25, ry - 18, (60, 120, 200)),
            (rx + 58, ry - 18, (80, 160, 90)),
            (rx + 91, ry - 18, (180, 140, 60)),
        ]
        for cx, cy, color in chars:
            pygame.draw.rect(screen, color, (cx, cy, 18, 22), border_radius=3)
            pygame.draw.circle(screen, (240, 210, 180), (cx + 9, cy - 5), 7)

    def _draw_victory_screen(self, screen):
        self._draw_victory_background(screen)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 30, 40, int(self.overlay_alpha)))
        screen.blit(overlay, (0, 0))

        title = "Поздравляю, вы прошли игру"
        alpha = max(0, min(255, int(self.text_alpha)))
        if alpha > 0:
            shadow = self.font_big.render(title, True, (0, 0, 0))
            shadow.set_alpha(alpha)
            text = self.font_big.render(title, True, (255, 245, 180))
            text.set_alpha(alpha)
            cx = WIDTH // 2
            screen.blit(shadow, shadow.get_rect(center=(cx + 3, 203)))
            screen.blit(text, text.get_rect(center=(cx, 200)))

        if self.text_alpha > 120:
            self.menu_btn.draw(screen, self.font)

    def draw(self, screen):
        if self.phase == "victory":
            self._draw_victory_screen(screen)
            return

        self._draw_sail_background(screen)
        self._draw_raft(screen)

        if self.phase == "board":
            font = pygame.font.SysFont(None, 28)
            text = font.render("Вы садитесь на плот...", True, (255, 255, 230))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 40))

        if self.fade_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.fade_alpha)))
            screen.blit(overlay, (0, 0))
