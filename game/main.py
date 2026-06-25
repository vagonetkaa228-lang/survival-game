import pygame
import game.settings as gs
from game.scenes.menu import MenuScene

pygame.init() # Инициализация Pygame
screen = pygame.display.set_mode((gs.WIDTH, gs.HEIGHT)) # Создание окна
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()
scene = MenuScene()# Текущая сцена (меню)
running = True

while running:
    clock.tick(gs.FPS)  # Ограничиваем частоту кадров

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Выход при закрытии окна

        new_scene = scene.handle_event(event)  # Обрабатываем событие текущей сценой
        if new_scene:
            scene = new_scene  # Переключаемся на новую сцену если вернулась

    new_scene = scene.update()  # Обновляем логику сцены
    if new_scene:
        scene = new_scene  # Переключаемся на новую сцену если вернулась

    scene.draw(screen)  # Отрисовываем сцену
    pygame.display.flip()  # Обновляем экран

pygame.quit()  # Завершаем работу Pygame