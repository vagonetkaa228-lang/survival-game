import pygame # для графики и событий
import math # для тригонометрических вычислений (фон)
import game.settings as gs # настройки игры (громкость)
from game.scenes.game_scene import GameScene # игровая сцена
from game.save_system import load_game # загрузка сохранения
from game.scenes.settings import SettingsScene # сцена настроек
from game.ui.button import Button # класс кнопки
from game.story.prologue import PrologueScene # сцена пролога

class MenuScene:
    def __init__(self):
        self.font_big = pygame.font.SysFont(None, 90) # большой шрифт для заголовка
        self.font = pygame.font.SysFont(None, 36) # обычный шрифт для кнопок

        self.start_btn = Button("Новая игра", 100, 270, 600, 60) # кнопка новой игры
        self.load_btn = Button("Загрузить", 100, 350, 600, 60) # кнопка загрузки
        self.settings = Button("Настройки", 100, 430 , 600, 60) # кнопка настроек

        self.time = 0 # время для анимации фона

        if not pygame.mixer.music.get_busy(): # если музыка не играет
            try:
                pygame.mixer.music.load("assets/music/menu.mp3") # загружаем трек меню
                pygame.mixer.music.set_volume(gs.SOUND_VOLUME) # устанавливаем громкость из настроек
                pygame.mixer.music.play(-1) # бесконечное зацикливание
                self._menu_music_playing = True # флаг, что музыка меню играет
            except Exception as e:
                print(f"Не удалось загрузить музыку: {e}") # ошибка не ломает игру

    def handle_event(self, event):
        if self.start_btn.clicked(event): # если нажали "Новая игра"
            pygame.mixer.music.stop() # останавливаем музыку меню
            return PrologueScene() # переходим в пролог

        if self.load_btn.clicked(event): # если нажали "Загрузить"
            pygame.mixer.music.stop() # останавливаем музыку меню
            data = load_game() # загружаем данные сохранения
            return GameScene(data) # переходим в игровую сцену с загруженными данными
        if self.settings.clicked(event): # если нажали "Настройки"
            return SettingsScene() # переходим в сцену настроек (музыка продолжает играть)

        return self # остаёмся в меню

    def update(self):
        self.time += 0.01 # увеличиваем счётчик времени для анимации

        self.start_btn.update() # обновляем кнопку (hover и т.п.)
        self.load_btn.update()
        self.settings.update()

    def draw(self, screen):
        # - АНИМИРОВАННЫЙ ФОН
        for y in range(600): # перебираем строки экрана по вертикали
            wave = int(10 * math.sin(self.time + y * 0.02)) # синусоидальная волна для цвета
            color = (15, 20 + y // 12 + wave, 40 + y // 10) # цвет меняется от тёмного к светлому
            pygame.draw.line(screen, color, (0, y), (800, y)) # рисуем горизонтальную линию

        # -ДЫМ / ПЛАВАЮЩИЕ ЧАСТИЦЫ
        for i in range(20): # 20 частиц
            x = (i * 120 + int(self.time * 50)) % 800 # X сдвигается со временем
            y = (i * 70) % 600 # Y распределён по экрану
            pygame.draw.circle(screen, (255, 255, 255, 20), (x, y), 2) # маленькая белая точка с прозрачностью

        #  ЗАГОЛОВОК
        shadow = self.font_big.render("LAST BREATHE", True, (0, 0, 0)) # тень заголовка
        title = self.font_big.render("LAST BREATHE", True, (255, 255, 255)) # сам заголовок

        screen.blit(shadow, (170, 152)) # рисуем тень со смещением
        screen.blit(title, (160, 150)) # рисуем заголовок

        # КНОПКИ
        self.start_btn.draw(screen, self.font) # рисуем кнопку новой игры
        self.load_btn.draw(screen, self.font) # рисуем кнопку загрузки
        self.settings.draw(screen, self.font) # рисуем кнопку настроек