import pygame
from game.ui.button import Button
from game.save_system import load_game
from game.scenes.game_scene import GameScene
from game.scenes.menu import MenuScene
import math

# class Button:
#     def __init__(self, text, x, y, w, h):
#         self.text = text
#         self.base_rect = pygame.Rect(x, y, w, h)
#         self.rect = self.base_rect.copy()
#         self.base_color = (50, 50, 80)
#         self.hover_color = (120, 120, 200)
#         self.scale = 1.0
#         self.target_scale = 1.0
#
#     def update(self):
#         self.scale += (self.target_scale - self.scale) * 0.15
#         center = self.base_rect.center
#         new_w = int(self.base_rect.width * self.scale)
#         new_h = int(self.base_rect.height * self.scale)
#         self.rect = pygame.Rect(0, 0, new_w, new_h)
#         self.rect.center = center
#
#     def draw(self, screen, font):
#         mouse = pygame.mouse.get_pos()
#         if self.rect.collidepoint(mouse):
#             self.target_scale = 1.08
#             color = self.hover_color
#         else:
#             self.target_scale = 1.0
#             color = self.base_color
#
#         shadow = self.rect.copy()
#         shadow.y += 6
#         pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)
#         pygame.draw.rect(screen, color, self.rect, border_radius=12)
#         pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)
#
#         text_surf = font.render(self.text, True, (255, 255, 255))
#         text_rect = text_surf.get_rect(center=self.rect.center)
#         screen.blit(text_surf, text_rect)
#
#     def clicked(self, event):
#         return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class GameOverScene:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 36)
        self.alpha = 0
        self.target_alpha = 180
        self.time = 0

        # Кнопки по центру экрана
        screen_center_x = 800 // 2
        self.btn_menu = Button("В главное меню", screen_center_x - 300, 300, 600, 60,
                               base_color=(80, 20, 20),
                               hover_color=(160, 40, 40))
        self.btn_load = Button("Загрузить последнее сохранение", screen_center_x - 300, 390, 600, 60,
                               base_color=(80, 20, 20),
                               hover_color=(160, 40, 40))

    def handle_event(self, event):
        if self.btn_menu.clicked(event):
            return MenuScene()
        if self.btn_load.clicked(event):
            data = load_game()
            if data:
                return GameScene(data)
            else:
                print("Сохранение не найдено!")
        return self

    def update(self):
        self.time += 0.01
        self.alpha += (self.target_alpha - self.alpha) * 0.1
        self.btn_menu.update()
        self.btn_load.update()

    def draw(self, screen):
            # ---------- АНИМИРОВАННЫЙ ФОН (КРАСНЫЙ) ----------
            for y in range(screen.get_height()):
                wave = int(8 * math.sin(self.time + y * 0.02))
                # Красные оттенки: от тёмно-бордового до чёрного
                r = min(40 + y // 10 + wave, 80)
                g = 0
                b = 0
                color = (r, g, b)
                pygame.draw.line(screen, color, (0, y), (screen.get_width(), y))

            # Плавающие частицы (как в меню)
            for i in range(20):
                x = (i * 120 + int(self.time * 50)) % screen.get_width()
                y = (i * 70) % screen.get_height()
                pygame.draw.circle(screen, (150, 30, 30, 30), (x, y), 2)

            # Затемняющий overlay с плавным появлением (уже был)
            overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, int(self.alpha)))
            screen.blit(overlay, (0, 0))

            # Текст GAME OVER
            text = self.font_big.render("ВЫ ПОГИБЛИ", True, (255, 80, 80))
            text_rect = text.get_rect(center=(screen.get_width() // 2, 200))
            # Добавим тень тексту
            shadow = self.font_big.render("ВЫ ПОГИБЛИ", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(screen.get_width() // 2 + 4, 204))
            screen.blit(shadow, shadow_rect)
            screen.blit(text, text_rect)

            # Кнопки
            self.btn_menu.draw(screen, self.font)
            self.btn_load.draw(screen, self.font)