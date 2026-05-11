import pygame

class Structure:
    def __init__(self, x, y, structure_type, width=40, height=40, solid=False):
        self.x = x
        self.y = y
        self.type = structure_type
        self.width = width
        self.height = height
        self.solid = solid
        self.health = 100
        self.max_health = 100
        self.is_open = False if structure_type == "door" else None  # только для дверей
        self.hit_timer = 0

    def toggle(self):
        """Переключить состояние двери (открыть/закрыть)"""
        if self.type == "door":
            self.is_open = not self.is_open
            self.solid = not self.is_open  # когда открыта – не твердая

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, player, enemies):
        pass

    def draw(self, surface, camera_x, camera_y, brightness=1.0):
        # сила подсветки (0..1)
        flash = min(1.0, self.hit_timer / 5.0)

        if self.type == "campfire":
            # Сияние: несколько кругов с уменьшающейся альфой
            if brightness < 0.7:  # проявляется только ночью/сумерках
                alpha = int((0.7 - brightness) * 300)  # чем темнее, тем ярче
                for radius_factor in [3, 5, 7]:
                    glow_radius = self.width // 2 * radius_factor
                    glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 200, 100, alpha // radius_factor),
                                       (glow_radius, glow_radius), glow_radius)
                    surface.blit(glow_surf, (self.x - camera_x - glow_radius + self.width // 2,
                                             self.y - camera_y - glow_radius + self.height // 2))
            # Основной круг
            color = (int(255 * brightness), int(140 * brightness), 0)
            pygame.draw.circle(surface, color,
                               (int(self.x + self.width // 2 - camera_x),
                                int(self.y + self.height // 2 - camera_y)),
                               self.width // 2)

        elif self.type == "tree":
            # Ствол
            trunk = (101, 67, 33)
            if flash:
                trunk = tuple(min(255, c + int(150 * flash)) for c in trunk)
            trunk_color = tuple(int(c * brightness) for c in trunk)
            trunk_rect = pygame.Rect(self.x - camera_x + 5,
                                     self.y - camera_y + 10, 10, 20)
            pygame.draw.rect(surface, trunk_color, trunk_rect)

            # Крона
            crown = (0, 100, 0)
            if flash:
                crown = tuple(min(255, c + int(150 * flash)) for c in crown)
            crown_color = tuple(int(c * brightness) for c in crown)
            crown_center = (self.x - camera_x + 10, self.y - camera_y + 5)
            pygame.draw.circle(surface, crown_color, crown_center, 15)

        elif self.type == "stone_vein":
            stone = (128, 128, 128)
            if flash:
                stone = tuple(min(255, c + int(150 * flash)) for c in stone)
            color = tuple(int(c * brightness) for c in stone)
            pygame.draw.rect(surface, color,
                             (self.x - camera_x, self.y - camera_y,
                              self.width, self.height))

        else:  # wall, door
            if self.type == "door":
                base = (0, 200, 0) if self.is_open else (139, 90, 43)
            else:
                base = (101, 67, 33)
            if flash:
                base = tuple(min(255, c + int(150 * flash)) for c in base)
            color = tuple(int(c * brightness) for c in base)
            pygame.draw.rect(surface, color,
                             (self.x - camera_x, self.y - camera_y,
                              self.width, self.height))