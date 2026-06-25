import pygame
import math

class WorldRenderer:
    def __init__(self, environment, hud):
        self.environment = environment
        self.hud = hud

    def draw_entities(self, surface, camera, player, enemies, loots, survivors, day_night, structures=None):
        # тени временно отключены, так как WorldEnvironment больше их не рисует
        # self.environment.draw_shadow(surface, player.x, player.y, player.size, camera, day_night)

        # игрок
        player.draw(surface, camera.x, camera.y)

        for e in enemies:
            # self.environment.draw_shadow(surface, e.x, e.y, e.size, camera, day_night)
            e.draw(surface, camera.x, camera.y)

            # HP бар врага ...


        for loot in loots:
            loot.draw(surface, camera.x, camera.y)

        for s in survivors:
            if getattr(s, 'story_npc', False) or not s.found:
                s.draw(surface, camera.x, camera.y)

        if structures:
            brightness = day_night.get_brightness() if day_night else 1.0
            for s in structures:
                s.draw(surface, camera.x, camera.y, brightness)
        # ...

    def render_full(self, screen, camera, player, enemies, loots, survivors, day_night, structures=None):
        world_surface = pygame.Surface((camera.width, camera.height))
        self.environment.draw_background(world_surface, camera, day_night)
        self.draw_entities(world_surface, camera, player, enemies, loots, survivors, day_night, structures)

        camera.apply(world_surface, screen)
        # HUD рисуем после apply (в GameScene.draw)
        self.hud.draw(screen, player)