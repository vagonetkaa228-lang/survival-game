import pygame
import game.settings as gs


#На вайб кожено
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
        # определяем текущий индекс по значению FPS
        try:
            self.fps_index = self.fps_options.index(gs.FPS)
        except ValueError:
            self.fps_index = 0
            gs.FPS = self.fps_options[self.fps_index]

        self.fps_btn = Button(
            "FPS: " + ("Unlimited" if gs.FPS == 0 else str(gs.FPS)),
            300, 200, 220, 50
        )

        self.sound = gs.SOUND_VOLUME
        self.sound_btn = Button(
            f"Sound: {int(self.sound * 100)}%",
            300, 270, 220, 50
        )

        self.back_btn = Button("Назад", 300, 400, 220, 50)

    def handle_event(self, event):
        if self.fps_btn.clicked(event):
            self.fps_index = (self.fps_index + 1) % len(self.fps_options)
            gs.FPS = self.fps_options[self.fps_index]
            self.fps_btn.text = "FPS: Unlimited" if gs.FPS == 0 else f"FPS: {gs.FPS}"

        if self.sound_btn.clicked(event):
            self.sound = (self.sound + 0.1) % 1.1
            self.sound = min(self.sound, 1.0)
            gs.SOUND_VOLUME = self.sound
            self.sound_btn.text = f"Sound: {int(self.sound * 100)}%"
            # Применяем громкость ко всем текущим музыкальным каналам
            pygame.mixer.music.set_volume(gs.SOUND_VOLUME)
            # Если есть дополнительные звуковые каналы – можно применить и к ним,
            # но в проекте используется только музыка.

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