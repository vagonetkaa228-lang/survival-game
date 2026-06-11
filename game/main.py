import pygame
from game.settings import WIDTH, HEIGHT
from game.scenes.menu import MenuScene

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survival Game")
clock = pygame.time.Clock()

scene = MenuScene()
running = True

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        new_scene = scene.handle_event(event)
        if new_scene:
            scene = new_scene


    new_scene = scene.update()
    if new_scene:
        scene = new_scene

    scene.draw(screen)
    pygame.display.flip()

pygame.quit()