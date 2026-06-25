import pygame
import random
import math
class DayNightCycle:
    def __init__(self, speed=None, day_duration=120, night_duration=60):
        """
        Параметры:
            speed – если передан, используется старый симметричный режим.
            day_duration – длительность дня в секундах (по умолчанию 120)
            night_duration – длительность ночи в секундах (по умолчанию 60)
        """
        self.time = 0.0
        self.speed = speed
        self.day_duration = day_duration
        self.night_duration = night_duration
        self.total_duration = day_duration + night_duration
        self.day_fraction = day_duration / self.total_duration
        self.use_asymmetric = (speed is None)

    def update(self, dt=1/60):
        if self.use_asymmetric:
            # Увеличиваем время пропорционально реальному времени
            self.time += dt / self.total_duration
            if self.time > 1.0:
                self.time -= 1.0
        else:
            self.time += self.speed
            if self.time > 1.0:
                self.time -= 1.0

    def get_brightness(self):
        if self.use_asymmetric:
            t = self.time
            if t < self.day_fraction:
                # День: яркость плавно падает от 1.0 до 0.5
                u = t / self.day_fraction
                # используем кубический сглаживающий полином для мягкого перехода
                u2 = u * u * (3 - 2 * u)  # smoothstep
                return 1.0 - 0.5 * u2
            else:
                # Ночь: яркость падает от 0.5 до 0.0
                u = (t - self.day_fraction) / (1.0 - self.day_fraction)
                u2 = u * u * (3 - 2 * u)
                return 0.5 * (1.0 - u2)
        else:
            # старый симметричный режим
            return 0.5 + 0.5 * math.sin(self.time * 2 * math.pi)

    def get_sun_direction(self):
        # В асимметричном режиме можно оставить синусоидальный угол,
        # либо адаптировать под фактическое положение солнца (но это не критично)
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
        """Деревья по сетке и жилы камней (как раньше)."""
        structures = []

        step = 80
        for x in range(self.center_x - int(self.island_radius_x), self.center_x + int(self.island_radius_x), step):
            for y in range(self.center_y - int(self.island_radius_y), self.center_y + int(self.island_radius_y), step):
                pos_x = x + random.randint(-10, 10)
                pos_y = y + random.randint(-10, 10)
                if self.get_tile(pos_x, pos_y) == 'grass':
                    if random.random() < 0.4:
                        structures.append(self.create_tree(pos_x, pos_y))

        for _ in range(10):
            vein_x = random.randint(self.center_x - int(self.island_radius_x * 0.7),
                                    self.center_x + int(self.island_radius_x * 0.7))
            vein_y = random.randint(self.center_y - int(self.island_radius_y * 0.7),
                                    self.center_y + int(self.island_radius_y * 0.7))
            for _ in range(random.randint(3, 8)):
                stone_x = vein_x + random.randint(-25, 25)
                stone_y = vein_y + random.randint(-25, 25)
                if self.get_tile(stone_x, stone_y) == 'grass':
                    structures.append(self.create_stone(stone_x, stone_y))

        return structures

    def generate_berry_loots(self):
        """Ягоды по карте: кластеры 1–2 штуки."""
        from game.entities.loot import Loot

        loots = []
        berry_centers = []
        cluster_spacing = 110
        cluster_radius = 30

        for _ in range(70):
            center = self._random_land_position()
            if center is None:
                continue
            cx, cy = center
            if any(math.hypot(cx - ox, cy - oy) < cluster_spacing for ox, oy in berry_centers):
                continue
            berry_centers.append((cx, cy))
            placed = 0
            target = random.randint(1, 2)
            for _ in range(target * 4):
                if placed >= target:
                    break
                ox = cx + random.randint(-cluster_radius, cluster_radius)
                oy = cy + random.randint(-cluster_radius, cluster_radius)
                if self.get_tile(ox, oy) not in ("grass", "sand"):
                    continue
                loots.append(Loot(ox, oy, "berry"))
                placed += 1

        return loots

    def generate_pebble_loots(self):
        """Камушки на карте: подбираются, дают камень (кластеры 1–2)."""
        from game.entities.loot import Loot

        loots = []
        pebble_centers = []
        cluster_spacing = 110
        cluster_radius = 30

        for _ in range(65):
            center = self._random_land_position()
            if center is None:
                continue
            cx, cy = center
            if any(math.hypot(cx - ox, cy - oy) < cluster_spacing for ox, oy in pebble_centers):
                continue
            pebble_centers.append((cx, cy))
            placed = 0
            target = random.randint(1, 2)
            for _ in range(target * 4):
                if placed >= target:
                    break
                ox = cx + random.randint(-cluster_radius, cluster_radius)
                oy = cy + random.randint(-cluster_radius, cluster_radius)
                if self.get_tile(ox, oy) not in ("grass", "sand"):
                    continue
                loots.append(Loot(ox, oy, "stone"))
                placed += 1

        return loots

    def _random_land_position(self, attempts=80):
        min_x = self.center_x - int(self.island_radius_x * 0.92)
        max_x = self.center_x + int(self.island_radius_x * 0.92)
        min_y = self.center_y - int(self.island_radius_y * 0.92)
        max_y = self.center_y + int(self.island_radius_y * 0.92)
        for _ in range(attempts):
            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            if self.get_tile(x, y) in ("grass", "sand"):
                return x, y
        return None

    def create_tree(self, x, y):
        from game.entities.structure import Structure
        from game.systems.mining import TREE_MAX_HP
        tree = Structure(x - 15, y - 30, "tree", width=30, height=30, solid=True)
        tree.health = TREE_MAX_HP
        tree.max_health = TREE_MAX_HP
        return tree

    def create_stone(self, x, y):
        from game.entities.structure import Structure
        from game.systems.mining import STONE_MAX_HP
        stone = Structure(x - 15, y - 15, "stone_vein", width=30, height=30, solid=True)
        stone.health = STONE_MAX_HP
        stone.max_health = STONE_MAX_HP
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

    def find_land_near(self, base_x, base_y, prefer=('sand', 'grass'), search_radius=None):
        """Ищет сушу рядом с точкой. Возвращает (world_x, world_y)."""
        if search_radius is None:
            search_radius = int(min(self.island_radius_x, self.island_radius_y) * 0.35)
        if self.get_tile(base_x, base_y) in prefer:
            return base_x, base_y
        step = 20
        for radius in range(step, search_radius + step, step):
            for dy in range(-radius, radius + 1, step):
                for dx in range(-radius, radius + 1, step):
                    if abs(dx) != radius and abs(dy) != radius:
                        continue
                    wx, wy = base_x + dx, base_y + dy
                    if self.get_tile(wx, wy) in prefer:
                        return wx, wy
        return base_x, base_y

    def get_crash_site_world_pos(self):
        """Место крушения на левом берегу острова (мировые координаты)."""
        base_x = self.center_x - int(self.island_radius_x * 0.75)
        base_y = self.center_y + int(self.island_radius_y * 0.35)
        return self.find_land_near(base_x, base_y, prefer=('sand', 'grass'))

    def get_game_spawn_after_prologue(self):
        """Стартовая позиция после пролога: левее и выше центра острова."""
        rx, ry = int(self.island_radius_x), int(self.island_radius_y)
        cx, cy = self.center_x, self.center_y
        for y in range(cy - int(ry * 0.35), cy + ry // 10, 25):
            for x in range(cx - int(rx * 0.65), cx - rx // 5, 25):
                if self.get_tile(x, y) == 'grass':
                    return x, y
        return self.find_land_near(cx - rx // 2, cy - ry // 8, prefer=('grass', 'sand'))

    def generate_beach_wreckage(self, count_range=(8, 12)):
        """Статичные обломки в верхнем левом углу острова."""
        from game.story.helicopter import StaticWreckage
        rx = int(self.island_radius_x)
        ry = int(self.island_radius_y)
        cx, cy = self.center_x, self.center_y
        base_x = cx - int(rx * 0.72)
        base_y = cy - int(ry * 0.72)
        wreckages = []
        target = random.randint(*count_range)
        attempts = 0
        while len(wreckages) < target and attempts < target * 50:
            attempts += 1
            wx = base_x + random.randint(-50, 120)
            wy = base_y + random.randint(-40, 100)
            if wx > cx - rx * 0.2 or wy > cy - ry * 0.15:
                continue
            tile = self.get_tile(wx, wy)
            if tile not in ('sand', 'grass'):
                continue
            new_rect = pygame.Rect(wx, wy, 30, 22)
            if any(w.rect.colliderect(new_rect) for w in wreckages):
                continue
            wreckages.append(StaticWreckage(wx, wy))
        return wreckages

    def is_near_crash_site(self, world_x, world_y, radius=110):
        cx, cy = self.get_crash_site_world_pos()
        return math.hypot(world_x - cx, world_y - cy) <= radius

    def get_pilot_rest_position(self):
        """Примерная позиция пилота после первого эпизода."""
        cx, cy = self.center_x, self.center_y
        rx, ry = int(self.island_radius_x), int(self.island_radius_y)
        for y in range(cy - ry // 4, cy + ry // 4, 25):
            for x in range(cx - int(rx * 0.55), cx - rx // 6, 25):
                if self.get_tile(x, y) == "grass":
                    return x, y
        return cx - rx // 3, cy

    def get_captain_rescue_site(self, pilot_x=None, pilot_y=None):
        """Место капитана: юго-восточный берег относительно пилота или острова."""
        if pilot_x is not None and pilot_y is not None:
            for dist in range(350, 1100, 45):
                for angle_deg in (15, 25, 35, 45, 55):
                    rad = math.radians(angle_deg)
                    sx = pilot_x + dist * math.cos(rad)
                    sy = pilot_y + dist * math.sin(rad)
                    if self.get_tile(sx, sy) not in ("sand", "grass"):
                        continue
                    water_pos = self._water_beside(sx, sy)
                    if water_pos:
                        wx, wy = water_pos
                        return {"shore_x": sx, "shore_y": sy, "water_x": wx, "water_y": wy}

        cx, cy = self.center_x, self.center_y
        rx, ry = int(self.island_radius_x), int(self.island_radius_y)
        best_shore = None
        best_score = -1
        for y in range(cy + ry // 6, cy + ry - 30, 20):
            for x in range(cx + rx // 5, cx + rx - 30, 20):
                if self.get_tile(x, y) not in ("sand", "grass"):
                    continue
                if not self._water_beside(x, y):
                    continue
                score = (x - cx) * 1.2 + (y - cy)
                if score > best_score:
                    best_score = score
                    best_shore = (x, y)

        if best_shore:
            shore_x, shore_y = best_shore
        else:
            shore_x = cx + int(rx * 0.55)
            shore_y = cy + int(ry * 0.55)
            shore_x, shore_y = self.find_land_near(shore_x, shore_y, prefer=("sand", "grass"))

        water_pos = self._water_beside(shore_x, shore_y)
        if water_pos:
            water_x, water_y = water_pos
        else:
            water_x, water_y = shore_x + 40, shore_y + 35

        return {"shore_x": shore_x, "shore_y": shore_y, "water_x": water_x, "water_y": water_y}

    def _water_beside(self, shore_x, shore_y):
        for step in range(20, 140, 10):
            for wx, wy in (
                (shore_x + step, shore_y + step // 2),
                (shore_x + step, shore_y),
                (shore_x + step // 2, shore_y + step),
            ):
                if self.get_tile(wx, wy) == "water":
                    return wx, wy
        return None
