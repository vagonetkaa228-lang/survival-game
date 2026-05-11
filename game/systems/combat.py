import math
from game.items.registry import ITEMS
from game.entities.projectiles import Projectile


def perform_attack(player, enemies, mouse_pos, camera, projectiles):
    if not player.active_item_id:
        return False

    item = ITEMS.get(player.active_item_id)
    if not item or not hasattr(item, 'tool_type'):
        return False

    world_click_x = mouse_pos[0] / camera.zoom + camera.x
    world_click_y = mouse_pos[1] / camera.zoom + camera.y
    px = player.x + player.size // 2
    py = player.y + player.size // 2

    if item.tool_type == "bow":
        _bow_attack(player, px, py, world_click_x, world_click_y, projectiles)
        return True
    elif item.tool_type == "gun":
        _gun_attack(player, item, px, py, world_click_x, world_click_y, projectiles)
        return True
    elif item.tool_type == "spear":
        _spear_attack(player, enemies, mouse_pos)
        return True

    return False


def _bow_attack(player, px, py, target_x, target_y, projectiles):
    arrow_id = "arrow"
    if player.count_item(arrow_id) > 0:          # ← правильно
        player.remove_item(arrow_id, 1)
        angle = math.atan2(target_y - py, target_x - px)
        proj = Projectile(px, py, angle, speed=10, damage=40)
        projectiles.append(proj)


# combat.py (фрагмент)
def _gun_attack(player, item, px, py, target_x, target_y, projectiles):
    stack = player.inventory.get(player.active_item_id)
    if stack and stack.durability and stack.durability > 0:
        player.consume_tool_durability(player.active_item_id)
        angle = math.atan2(target_y - py, target_x - px)
        proj = Projectile(px, py, angle, speed=15, damage=15)
        projectiles.append(proj)

def _spear_attack(player, enemies, mouse_pos):
    old_range = player.attack_range
    player.attack_range = 70
    player.attack(enemies, mouse_pos)
    player.attack_range = old_range


def _break_active_item(player):
    player.remove_item(player.active_item_id, 1)
    player.active_item_id = None