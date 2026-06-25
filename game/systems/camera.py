import pygame

class Camera:
    def __init__(self, width, height, world_width, world_height):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.target_x = 0
        self.target_y = 0
        self.width = width
        self.height = height
        self.world_width = world_width
        self.world_height = world_height

    def update(self, player_x, player_y, smooth_factor=0.1):
        self.target_x = player_x - self.width // 2
        self.target_y = player_y - self.height // 2

        self.target_x = max(0, min(self.target_x, self.world_width - self.width))
        self.target_y = max(0, min(self.target_y, self.world_height - self.height))

        self.x += (self.target_x - self.x) * smooth_factor
        self.y += (self.target_y - self.y) * smooth_factor

    def handle_zoom(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.zoom += event.y * 0.1
            self.zoom = max(0.5, min(2.0, self.zoom))

    def apply(self, surface, screen):
        scaled = pygame.transform.scale(
            surface,
            (int(self.width * self.zoom), int(self.height * self.zoom))
        )
        screen.blit(
            scaled,
            (
                -(scaled.get_width() - self.width) // 2,
                -(scaled.get_height() - self.height) // 2
            )
        )

    def world_to_screen(self, world_x, world_y):
        """Перевод мировых координат в экранные с учётом зума."""
        ox = -(int(self.width * self.zoom) - self.width) // 2
        oy = -(int(self.height * self.zoom) - self.height) // 2
        sx = int((world_x - self.x) * self.zoom + ox)
        sy = int((world_y - self.y) * self.zoom + oy)
        return sx, sy