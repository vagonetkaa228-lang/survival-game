import pygame  # Для работы с графикой и событиями

class Button:
    def __init__(self, text, x, y, w, h,
                 base_color=(50, 50, 80),
                 hover_color=(120, 120, 200),
                 text_color=(255, 255, 255),
                 border_color=(255, 255, 255)):
        """Создаёт кнопку с текстом, позицией, размером и цветами"""
        self.text = text  # Текст на кнопке
        self.base_rect = pygame.Rect(x, y, w, h)  # Базовый прямоугольник (без масштаба)
        self.rect = self.base_rect.copy()  # Текущий прямоугольник (с учётом масштаба)
        self.base_color = base_color  # Цвет кнопки в обычном состоянии
        self.hover_color = hover_color  # Цвет при наведении
        self.text_color = text_color  # Цвет текста
        self.border_color = border_color  # Цвет рамки
        self.scale = 1.0  # Текущий масштаб
        self.target_scale = 1.0  # Целевой масштаб (для анимации увеличения)

    def update(self):
        """Плавно изменяет масштаб кнопки для анимации при наведении"""
        self.scale += (self.target_scale - self.scale) * 0.15  # Плавное приближение к цели
        center = self.base_rect.center  # Сохраняем центр
        new_w = int(self.base_rect.width * self.scale)  # Новая ширина с учётом масштаба
        new_h = int(self.base_rect.height * self.scale)  # Новая высота с учётом масштаба
        self.rect = pygame.Rect(0, 0, new_w, new_h)  # Создаём новый прямоугольник
        self.rect.center = center  # Возвращаем центр на место

    def draw(self, screen, font):
        """Отрисовывает кнопку с тенью, рамкой и текстом"""
        mouse = pygame.mouse.get_pos()  # Позиция мыши
        if self.rect.collidepoint(mouse):  # Если мышь над кнопкой
            self.target_scale = 1.08  # Увеличиваем кнопку
            color = self.hover_color  # Меняем цвет
        else:
            self.target_scale = 1.0  # Возвращаем обычный размер
            color = self.base_color  # Возвращаем обычный цвет

        # Тень (смещённый вниз чёрный прямоугольник)
        shadow = self.rect.copy()
        shadow.y += 6
        pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)

        # Основной прямоугольник кнопки
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        # Рамка кнопки
        pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=12)

        # Рендерим и отображаем текст по центру кнопки
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def clicked(self, event):
        """Проверяет, была ли нажата кнопка (событие клика мыши)"""
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)