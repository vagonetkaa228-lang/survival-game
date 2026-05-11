import pygame

class Button:
    def __init__(self, text, x, y, w, h,
                 base_color=(50, 50, 80),
                 hover_color=(120, 120, 200),
                 text_color=(255, 255, 255),
                 border_color=(255, 255, 255)):
        self.text = text
        self.base_rect = pygame.Rect(x, y, w, h)
        self.rect = self.base_rect.copy()
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.scale = 1.0
        self.target_scale = 1.0

    def update(self):
        self.scale += (self.target_scale - self.scale) * 0.15
        center = self.base_rect.center
        new_w = int(self.base_rect.width * self.scale)
        new_h = int(self.base_rect.height * self.scale)
        self.rect = pygame.Rect(0, 0, new_w, new_h)
        self.rect.center = center

    def draw(self, screen, font):
        mouse = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse):
            self.target_scale = 1.08
            color = self.hover_color
        else:
            self.target_scale = 1.0
            color = self.base_color

        # Тень
        shadow = self.rect.copy()
        shadow.y += 6
        pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)

        # Основной прямоугольник
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=12)

        # Текст
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)