import pygame
from game.settings import*

class Button:
    def __init__(self, text, x, y, w, h):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.base = (50, 50, 80)
        self.hover = (120, 120, 200)

    def draw(self, screen, font):
        color = self.hover if self.rect.collidepoint(pygame.mouse.get_pos()) else self.base

        pygame.draw.rect(screen, (0, 0, 0), self.rect.move(0, 5), border_radius=10)
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=10)

        txt = font.render(self.text, True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.rect.center))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

class SettingsScene:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.big = pygame.font.SysFont(None, 60)

        self.fps_options = [60, 120, 144, 0]
        self.fps_index = 0

        self.fps_btn = Button("FPS: 60", 300, 200, 220, 50)
        self.sound_btn = Button("Sound: 50%", 300, 270, 220, 50)
        self.back_btn = Button("Назад", 300, 400, 220, 50)

        self.sound = 0.5

    def handle_event(self, event):
        global FPS, SOUND_VOLUME

        if self.fps_btn.clicked(event):
            self.fps_index = (self.fps_index + 1) % len(self.fps_options)
            FPS = self.fps_options[self.fps_index]

            self.fps_btn.text = "FPS: Unlimited" if FPS == 0 else f"FPS: {FPS}"

        if self.sound_btn.clicked(event):
            self.sound = (self.sound + 0.1) % 1.1
            SOUND_VOLUME = min(self.sound, 1.0)
            self.sound_btn.text = f"Sound: {int(self.sound * 100)}%"

        if self.back_btn.clicked(event):
            from game.scenes.menu import MenuScene
            return MenuScene()

        return self

    def update(self):
        pass

    def draw(self, screen):
        screen.fill((20, 20, 40))

        title = self.big.render("SETTINGS", True, (255, 255, 255))
        screen.blit(title, (300, 100))

        self.fps_btn.draw(screen, self.font)
        self.sound_btn.draw(screen, self.font)
        self.back_btn.draw(screen, self.font)