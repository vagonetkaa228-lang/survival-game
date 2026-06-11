import pygame
import random

class HelicopterWreckage:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = random.randint(15, 50)
        self.height = random.randint(10, 30)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.solid = True
        self.fire_particles = []
        self.smoke_particles = []
        self._init_particles()

    def _init_particles(self):
        # Начальные частицы огня
        for _ in range(random.randint(3, 6)):
            self.fire_particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height * 0.5),
                'alpha': random.randint(100, 200),
                'size': random.uniform(2, 5),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-1.5, -0.5)
            })
        # Начальные частицы дыма
        for _ in range(random.randint(2, 4)):
            self.smoke_particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height * 0.5),
                'alpha': random.randint(80, 150),
                'size': random.uniform(4, 8),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-0.8, -0.2)
            })

    def update(self):
        # Обновление огня
        for p in self.fire_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 2
            if p['alpha'] <= 0:
                self.fire_particles.remove(p)
        if random.random() < 0.3:  # новые частицы огня
            self.fire_particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height * 0.5),
                'alpha': random.randint(150, 255),
                'size': random.uniform(2, 5),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-2, -1)
            })
        # Обновление дыма
        for p in self.smoke_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['alpha'] -= 1
            p['size'] += 0.1
            if p['alpha'] <= 0:
                self.smoke_particles.remove(p)
        if random.random() < 0.2:  # новые клубы дыма
            self.smoke_particles.append({
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height * 0.5),
                'alpha': random.randint(100, 200),
                'size': random.uniform(4, 8),
                'vx': random.uniform(-0.2, 0.2),
                'vy': random.uniform(-1, -0.5)
            })

    def draw(self, surface, camera_x, camera_y):
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        # Тёмно-зелёный корпус
        pygame.draw.rect(surface, (30, 80, 30), (screen_x, screen_y, self.width, self.height))
        # Металлическая окантовка
        pygame.draw.rect(surface, (50, 50, 50), (screen_x, screen_y, self.width, self.height), 2)
        # Огонь
        for p in self.fire_particles:
            alpha = max(0, min(255, int(p['alpha'])))
            size = int(p['size'])
            if size > 0:
                fire_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, (255, 100, 0, alpha), (size, size), size)
                surface.blit(fire_surf, (screen_x + p['x'] - size, screen_y + p['y'] - size))
        # Дым
        for p in self.smoke_particles:
            alpha = max(0, min(255, int(p['alpha'])))
            size = int(p['size'])
            if size > 0:
                smoke_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (150, 150, 150, alpha), (size, size), size)
                surface.blit(smoke_surf, (screen_x + p['x'] - size, screen_y + p['y'] - size))

    def get_rect(self):
        return self.rect