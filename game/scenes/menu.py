import pygame
import math
import game.settings as gs
from game.scenes.game_scene import GameScene
from game.save_system import load_game
from game.scenes.settings import SettingsScene
from game.ui.button import Button
from game.story.prologue import PrologueScene

class MenuScene:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 90)
        self.font = pygame.font.SysFont(None, 36)

        self.start_btn = Button("Новая игра", 100, 270, 600, 60)
        self.load_btn = Button("Загрузить", 100, 350, 600, 60)
        self.settings = Button("Настройки", 100, 430 , 600, 60)

        self.time = 0

        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load("assets/music/menu.mp3")
                pygame.mixer.music.set_volume(gs.SOUND_VOLUME)
                pygame.mixer.music.play(-1)
                self._menu_music_playing = True
            except Exception as e:
                print(f"Не удалось загрузить музыку: {e}")

    def handle_event(self, event):
        if self.start_btn.clicked(event):
            pygame.mixer.music.stop()
            return PrologueScene()

        if self.load_btn.clicked(event):
            pygame.mixer.music.stop()
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