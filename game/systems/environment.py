import pygame
import random
import math

class DayNightCycle:
    def __init__(self, speed=0.0005):
        self.time = 0.0
        self.speed = speed

    def update(self):
        self.time += self.speed
        if self.time > 1:
            self.time -= 1

    def get_brightness(self):
        return 0.5 + 0.5 * math.sin(self.time * 2 * math.pi)

    def get_sun_direction(self):
        angle = self.time * 2 * math.pi
        return (math.cos(angle), math.sin(angle))

class WorldEnvironment:
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        self.center_x = world_width // 2
        self.center_y = world_height // 2
        self.island_radius_x = world_width * 0.4   # примерно 800 при 2000
        self.island_radius_y = world_height * 0.4
        self.beach_width = 60

        # Сгенерируем карту высот для неровных краёв (шум Перлина упрощённый)
        self.noise = {}
        random.seed(42)  # фиксируем для воспроизводимости

    def get_noise(self, x, y):
        # Простая псевдослучайная функция для создания неровностей берега
        key = (x // 20, y // 20)  # группируем по клеткам 20x20
        if key not in self.noise:
            self.noise[key] = random.uniform(-15, 15)
        return self.noise[key]

    def get_tile(self, world_x, world_y):
        """Возвращает тип тайла в точке мира: 'water', 'sand', 'grass'"""
        dx = world_x - self.center_x
        dy = world_y - self.center_y
        # Эллипс острова
        ellipse_dist = (dx**2) / (self.island_radius_x**2) + (dy**2) / (self.island_radius_y**2)
        noise = self.get_noise(world_x, world_y)
        outer = 1.0 + noise / self.island_radius_x * 0.5  # примерно 1.0 +/- 0.01

        if ellipse_dist <= 1.0:
            return 'grass'
        elif ellipse_dist <= 1.0 + (self.beach_width / self.island_radius_x) * 1.5:
            # пляж: узкая полоса с переходом
            return 'sand'
        else:
            return 'water'

    def draw_background(self, surface, camera, day_night):
        """Рисует фон (воду, песок, траву) плитками 40x40"""
        brightness = day_night.get_brightness()
        tile_size = 40
        start_x = int(camera.x // tile_size) * tile_size
        start_y = int(camera.y // tile_size) * tile_size
        end_x = int(camera.x + camera.width) + tile_size
        end_y = int(camera.y + camera.height) + tile_size

        for y in range(start_y, end_y, tile_size):
            for x in range(start_x, end_x, tile_size):
                tile_type = self.get_tile(x + tile_size//2, y + tile_size//2)
                if tile_type == 'water':
                    color = (0, 0, 180 * brightness)
                elif tile_type == 'sand':
                    color = (194 * brightness, 178 * brightness, 128 * brightness)
                else:  # grass
                    color = (34 * brightness, 139 * brightness, 34 * brightness)
                draw_rect = pygame.Rect(x - camera.x, y - camera.y, tile_size, tile_size)
                pygame.draw.rect(surface, color, draw_rect)

    def generate_structures(self):
        """Создаёт список деревьев и камней (Structure) на основе карты.
        Возвращает список структур."""
        structures = []
        # Деревья: размещаем на траве с вероятностью, избегая краёв
        step = 200  # расстояние между возможными позициями
        for x in range(self.center_x - int(self.island_radius_x), self.center_x + int(self.island_radius_x), step):
            for y in range(self.center_y - int(self.island_radius_y), self.center_y + int(self.island_radius_y), step):
                # Добавим небольшой случайный сдвиг
                pos_x = x + random.randint(-10, 10)
                pos_y = y + random.randint(-10, 10)
                if self.get_tile(pos_x, pos_y) == 'grass':
                    # Не каждую клетку заполняем
                    if random.random() < 0.4:  # 40% шанс дерева
                        # Проверим, не слишком ли близко к камню (камни генерируются позже, но можно пропустить)
                        structures.append(self.create_tree(pos_x, pos_y))

        # Камни: генерируем несколько "жил" (скоплений камней)
        for _ in range(10):
            vein_x = random.randint(self.center_x - int(self.island_radius_x * 0.7),
                                    self.center_x + int(self.island_radius_x * 0.7))
            vein_y = random.randint(self.center_y - int(self.island_radius_y * 0.7),
                                    self.center_y + int(self.island_radius_y * 0.7))
            # Скопление из 3-8 камней
            for _ in range(random.randint(3, 8)):
                stone_x = vein_x + random.randint(-25, 25)
                stone_y = vein_y + random.randint(-25, 25)
                if self.get_tile(stone_x, stone_y) == 'grass':
                    structures.append(self.create_stone(stone_x, stone_y))
        return structures

    def create_tree(self, x, y):
        from game.entities.structure import Structure
        tree = Structure(x - 15, y - 30, "tree", width=30, height=30, solid=True)
        tree.health = 3  # пока неразрушимы, но можно задать
        return tree

    def create_stone(self, x, y):
        from game.entities.structure import Structure
        stone = Structure(x - 15, y - 15, "stone_vein", width=30, height=30, solid=True)
        stone.health = 5  # можно будет разбить
        return stone

    def is_land(self, world_x, world_y):
        """Возвращает True, если точка находится на суше (трава или песок)"""
        tile = self.get_tile(world_x, world_y)
        return tile != 'water'

    def is_land_fast(self, world_x, world_y):
        """Быстрая проверка без шума (только эллипс острова)"""
        dx = world_x - self.center_x
        dy = world_y - self.center_y
        ellipse_dist = (dx ** 2) / (self.island_radius_x ** 2) + (dy ** 2) / (self.island_radius_y ** 2)
        return ellipse_dist <= 1.0  # внутри эллипса – суша (трава), иначе вода
