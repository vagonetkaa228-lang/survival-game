import os
import pygame

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "images")
_raw_cache = {}
_scaled_cache = {}

ITEM_SPRITE_MAP = {
    "berry": "berry",
    "meat": "meat",
    "clean_water": "water",
    "dirty_water": "water",
    "wood": "wood",
    "stone": "stone",
    "stone_axe": "axe",
    "stone_pickaxe": "pickaxe",
    "spear": "spear",
    "bow": "bow",
    "arrow": "arrow",
    "pistol": "pistol",
    "magazine": "patron",
    "campfire": "fire",
    "campfire_kit": "fire",
    "wood_wall_kit": "wall",
    "wood_door_kit": "wall",
    "raft": "wood",

}

ENTITY_SPRITE_MAP = {
    "player": "player",
    "wolf": "wolf",
    "bear": "bear",
    "deer": "deer",
    "fox": "fox",
    "rabbit": "rabbiot",
    "pilot": "pilot",
    "captain": "capitan",
    "survivor": "player",
    "wall": "wall",
    "door": "wall",
    "campfire": "fire",
}


def _resolve_path(name):
    for ext in (".png", ".jpg", ".jpeg"):
        path = os.path.join(_ASSETS_DIR, name + ext)
        if os.path.isfile(path):
            return path
    return None


def _strip_background(image):
    """Убирает чёрный / однотонный фон у спрайтов."""
    image = image.convert_alpha()
    bg = image.get_at((0, 0))
    bg_r, bg_g, bg_b = bg[0], bg[1], bg[2]

    for y in range(image.get_height()):
        for x in range(image.get_width()):
            r, g, b, a = image.get_at((x, y))
            if r <= 35 and g <= 35 and b <= 35:
                image.set_at((x, y), (0, 0, 0, 0))
            elif (
                abs(r - bg_r) <= 14
                and abs(g - bg_g) <= 14
                and abs(b - bg_b) <= 14
            ):
                image.set_at((x, y), (0, 0, 0, 0))

    return image


def _load_raw(name):
    if name in _raw_cache:
        return _raw_cache[name]
    path = _resolve_path(name)
    if not path:
        _raw_cache[name] = None
        return None
    try:
        image = _strip_background(pygame.image.load(path))
    except pygame.error:
        image = None
    _raw_cache[name] = image
    return image


def get_sprite(name, size=None):
    if size is None:
        return _load_raw(name)

    key = (name, size)
    if key in _scaled_cache:
        return _scaled_cache[key]

    raw = _load_raw(name)
    if raw is None:
        _scaled_cache[key] = None
        return None

    if isinstance(size, int):
        w = h = size
    else:
        w, h = size

    scaled = pygame.transform.smoothscale(raw, (max(1, int(w)), max(1, int(h))))
    _scaled_cache[key] = scaled
    return scaled


def get_item_sprite_name(item_id):
    return ITEM_SPRITE_MAP.get(item_id, "drop")


def get_entity_sprite_name(entity_type):
    return ENTITY_SPRITE_MAP.get(entity_type, "drop")


def blit_sprite(
    surface,
    sprite_name,
    world_x,
    world_y,
    size,
    camera_x=0,
    camera_y=0,
    *,
    hit=False,
    dying=False,
    brightness=1.0,
):
    sprite = get_sprite(sprite_name, size)
    screen_x = int(world_x - camera_x)
    screen_y = int(world_y - camera_y)

    if sprite is None:
        w = size if isinstance(size, int) else size[0]
        h = size if isinstance(size, int) else size[1]
        color = (200, 60, 60) if dying else (255, 255, 255) if hit else (160, 160, 160)
        pygame.draw.rect(surface, color, (screen_x, screen_y, w, h))
        return

    if hit or dying or brightness < 0.99:
        image = sprite.copy()
        if brightness < 0.99:
            shade = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            alpha = int(255 * (1.0 - brightness * 0.55))
            shade.fill((0, 0, 30, alpha))
            image.blit(shade, (0, 0))
        if hit:
            flash = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 140))
            image.blit(flash, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        if dying:
            tint = pygame.Surface(image.get_size(), pygame.SRCALPHA)
            tint.fill((120, 0, 0, 110))
            image.blit(tint, (0, 0))
        surface.blit(image, (screen_x, screen_y))
    else:
        surface.blit(sprite, (screen_x, screen_y))


def blit_entity(surface, entity_type, world_x, world_y, size, camera_x, camera_y, **kwargs):
    name = get_entity_sprite_name(entity_type)
    blit_sprite(surface, name, world_x, world_y, size, camera_x, camera_y, **kwargs)


def blit_item(surface, item_id, rect, size=None):
    name = get_item_sprite_name(item_id)
    if size is None:
        size = min(rect.width, rect.height) - 8
    sprite = get_sprite(name, size)
    if sprite is None:
        pygame.draw.rect(surface, (150, 150, 150), rect.inflate(-6, -6))
        return
    x = rect.x + (rect.width - sprite.get_width()) // 2
    y = rect.y + (rect.height - sprite.get_height()) // 2
    surface.blit(sprite, (x, y))
