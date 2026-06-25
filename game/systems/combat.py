import math # для вычисления угла (atan2)
from game.items.registry import ITEMS
from game.entities.projectiles import Projectile # класс снаряда

def perform_attack(player, enemies, mouse_pos, camera, projectiles):
    if not player.active_item_id: # если нет активного предмета
        return False # атака не выполнена

    item = ITEMS.get(player.active_item_id) # получаем объект предмета по id
    if not item or not hasattr(item, 'tool_type'): # если предмета нет или он не инструмент
        return False # не атакуем

    world_click_x = mouse_pos[0] / camera.zoom + camera.x # преобразуем координаты мыши в мировые X
    world_click_y = mouse_pos[1] / camera.zoom + camera.y # преобразуем координаты мыши в мировые Y
    px = player.x + player.size // 2 # центр игрока X
    py = player.y + player.size // 2 # центр игрока Y

    if item.tool_type == "bow": # если лук
        _bow_attack(player, px, py, world_click_x, world_click_y, projectiles) # стреляем из лука
        return True
    elif item.tool_type == "gun": # если пистолет
        _gun_attack(player, item, px, py, world_click_x, world_click_y, projectiles) # стреляем из пистолета
        return True
    elif item.tool_type == "spear": # если копьё
        _spear_attack(player, enemies, mouse_pos) # атакуем копьём (ближний бой)
        return True

    return False # не распознанный тип атаки

def _bow_attack(player, px, py, target_x, target_y, projectiles):
    arrow_id = "arrow" # id стрел
    if player.count_item(arrow_id) > 0: # если есть стрелы в инвентаре
        player.remove_item(arrow_id, 1) # расходуем одну стрелу
        angle = math.atan2(target_y - py, target_x - px) # угол к цели (в радианах)
        proj = Projectile(px, py, angle, speed=10, damage=80) # создаём снаряд
        projectiles.append(proj) # добавляем в список снарядов

def _gun_attack(player, item, px, py, target_x, target_y, projectiles):
    stack = player.get_stack(player.active_item_id) # получаем стак активного предмета
    if stack and stack.durability and stack.durability > 0: # если есть прочность > 0
        player.consume_tool_durability(player.active_item_id) # тратим одну единицу прочности
        angle = math.atan2(target_y - py, target_x - px) # угол к цели
        proj = Projectile(px, py, angle, speed=15, damage=100) # создаём снаряд (быстрее и сильнее)
        projectiles.append(proj) # добавляем в список

def _spear_attack(player, enemies, mouse_pos):
    old_range = player.attack_range # запоминаем старую дальность атаки игрока
    player.attack_range = 70 # временно увеличиваем дальность (для копья)
    player.attack(enemies, mouse_pos) # вызываем обычную атаку игрока с увеличенной дальностью
    player.attack_range = old_range # возвращаем исходную дальность

def _break_active_item(player):
    player.remove_item(player.active_item_id, 1) # удаляем один активный предмет из инвентаря
    player.active_item_id = None # сбрасываем активный предмет