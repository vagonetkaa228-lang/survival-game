import pygame
import math
from game.scenes.game_scene import GameScene
from game.save_system import load_game
from game.scenes.settings import SettingsScene
from game.ui.button import Button

# ---------------- BUTTON ----------------
# class Button:
#     def __init__(self, text, x, y, w, h):
#         self.text = text
#         self.base_rect = pygame.Rect(x, y, w, h)
#         self.rect = self.base_rect.copy()
#
#         self.base_color = (50, 50, 80)
#         self.hover_color = (120, 120, 200)
#
#         self.scale = 1.0
#         self.target_scale = 1.0
#
#     def update(self):
#         # плавная анимация (easing)
#         self.scale += (self.target_scale - self.scale) * 0.15
#
#         center = self.base_rect.center
#         new_w = int(self.base_rect.width * self.scale)
#         new_h = int(self.base_rect.height * self.scale)
#
#         self.rect = pygame.Rect(0, 0, new_w, new_h)
#         self.rect.center = center
#
#     def draw(self, screen, font):
#         mouse = pygame.mouse.get_pos()
#
#         if self.rect.collidepoint(mouse):
#             self.target_scale = 1.08
#             color = self.hover_color
#         else:
#             self.target_scale = 1.0
#             color = self.base_color
#
#         # тень
#         shadow = self.rect.copy()
#         shadow.y += 6
#         pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)
#
#         # кнопка
#         pygame.draw.rect(screen, color, self.rect, border_radius=12)
#         pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)
#
#         # текст
#         text_surf = font.render(self.text, True, (255, 255, 255))
#         text_rect = text_surf.get_rect(center=self.rect.center)
#         screen.blit(text_surf, text_rect)
#
#     def clicked(self, event):
#         return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# ---------------- MENU ----------------
class MenuScene:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 90)
        self.font = pygame.font.SysFont(None, 36)

        self.start_btn = Button("Новая игра", 100, 270, 600, 60)
        self.load_btn = Button("Загрузить", 100, 350, 600, 60)
        self.settings = Button("Настройки", 100, 430 , 600, 60)

        self.time = 0

    def handle_event(self, event):
        if self.start_btn.clicked(event):
            return GameScene()

        if self.load_btn.clicked(event):
            data = load_game()
            return GameScene(data)
        if self.settings.clicked(event):
            return SettingsScene()

        return self

    def update(self):
        self.time += 0.01

        self.start_btn.update()
        self.load_btn.update()
        self.settings.update()

    def draw(self, screen):
        # --------- АНИМИРОВАННЫЙ ФОН ----------
        for y in range(600):
            wave = int(10 * math.sin(self.time + y * 0.02))
            color = (15, 20 + y // 12 + wave, 40 + y // 10)
            pygame.draw.line(screen, color, (0, y), (800, y))

        # --------- ДЫМ / ПЛАВАЮЩИЕ ЧАСТИЦЫ ----------
        for i in range(20):
            x = (i * 120 + int(self.time * 50)) % 800
            y = (i * 70) % 600
            pygame.draw.circle(screen, (255, 255, 255, 20), (x, y), 2)

        # --------- ЗАГОЛОВОК ----------
        shadow = self.font_big.render("LAST BREATHE", True, (0, 0, 0))
        title = self.font_big.render("LAST BREATHE", True, (255, 255, 255))

        screen.blit(shadow, (170, 152))
        screen.blit(title, (160, 150))

        # --------- КНОПКИ ----------
        self.start_btn.draw(screen, self.font)
        self.load_btn.draw(screen, self.font)
        self.settings.draw(screen, self.font)