import pygame


def draw_dialog_box(screen, author, text, font, small_font, dialog_index=0, total=1):
    bar_width = int(screen.get_width() * 0.9)
    bar_height = 140
    bar_x = (screen.get_width() - bar_width) // 2
    bar_y = (screen.get_height() - bar_height) // 2

    bar = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 200))
    screen.blit(bar, (bar_x, bar_y))
    pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height), 2)

    author_color = (255, 200, 100) if author != "Игрок" else (180, 220, 255)
    author_surf = font.render(author + ":", True, author_color)
    author_rect = author_surf.get_rect(center=(screen.get_width() // 2, bar_y + 30))
    screen.blit(author_surf, author_rect)

    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(screen.get_width() // 2, bar_y + 70))
    screen.blit(text_surf, text_rect)

    hint = small_font.render("E / Пробел — далее", True, (180, 180, 180))
    hint_rect = hint.get_rect(bottomright=(bar_x + bar_width - 10, bar_y + bar_height - 10))
    screen.blit(hint, hint_rect)
