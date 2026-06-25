import json  # Для сохранения/загрузки данных в формате JSON
from game.entities.player import INVENTORY_SIZE
from game.items.item_stack import ItemStack

SAVE_FILE = 'save.json'  # Имя файла сохранения


def _slots_from_legacy_inventory(inv_dict):

    from game.items.registry import ITEMS

    slots = [None] * INVENTORY_SIZE  # Создаём пустые слоты
    idx = 0  # Текущий индекс слота
    for item_id, stack in inv_dict.items():  # Перебираем предметы в старом инвентаре
        prototype = ITEMS.get(item_id)  # Получаем прототип предмета
        max_stack = prototype.max_stack if prototype else 99  # Максимальный размер стопки
        remaining = stack.count  # Сколько осталось разложить
        durability = stack.durability  # Прочность предмета
        while remaining > 0 and idx < INVENTORY_SIZE:  # Пока есть предметы и свободные слоты
            chunk = min(remaining, max_stack)  # Сколько поместится в один слот
            slots[idx] = ItemStack(item_id, chunk, durability)  # Создаём стопку
            remaining -= chunk  # Уменьшаем остаток
            idx += 1  # Переходим к следующему слоту
            if max_stack == 1:  # Если предмет не стакается (например, оружие)
                durability = None  # Прочность только у первого экземпляра
    return slots


def _serialize_player(player):
    """Превращает объект игрока в словарь для сохранения"""
    return {
        'x': player.x,  # Позиция по X
        'y': player.y,  # Позиция по Y
        'health': player.health,  # Здоровье
        'hunger': player.hunger,  # Голод
        'thirst': player.thirst,  # Жажда
        'energy': player.energy,  # Энергия
        'inventory_slots': [  # Инвентарь (список слотов)
            stack.to_dict() if stack else None  # Превращаем каждую стопку в словарь
            for stack in player.inventory_slots
        ],
        'hotbar': player.hotbar,  # Индексы слотов на панели быстрого доступа
        'active_item_id': player.active_item_id,  # Активный предмет
    }


def save_game(game_scene):
    """Сохраняет состояние игры в файл"""
    data = {
        'player': _serialize_player(game_scene.player),  # Данные игрока
        'tutorial_completed': game_scene.tutorial_completed,  # Пройден ли туториал
        'prologue_completed': game_scene.prologue_completed,  # Пройден ли пролог
        'pilot_rescue_completed': game_scene.pilot_rescue_completed,  # Спасён ли пилот
        'captain_rescue_completed': game_scene.captain_rescue_completed,  # Спасён ли капитан
        'unlocked_story_recipes': list(game_scene.unlocked_story_recipes),  # Открытые рецепты
        'spawn_x': game_scene.player.x,  # Точка возрождения X
        'spawn_y': game_scene.player.y,  # Точка возрождения Y
    }
    with open(SAVE_FILE, 'w') as f:  # Открываем файл на запись
        json.dump(data, f)  # Записываем данные в JSON


def load_game():
    """Загружает состояние игры из файла, возвращает None если файла нет"""
    try:
        with open(SAVE_FILE, 'r') as f:  # Открываем файл на чтение
            data = json.load(f)  # Загружаем данные из JSON

        player_data = data['player']  # Берём данные игрока

        # Пытаемся загрузить инвентарь в новом формате (список слотов)
        if 'inventory_slots' in player_data:
            player_data['inventory_slots'] = [
                ItemStack.from_dict(slot) if slot else None  # Восстанавливаем стопки из словарей
                for slot in player_data['inventory_slots']
            ]
        else:
            # Если инвентарь в старом формате (словарь) - конвертируем
            inv = {}
            for item_id, ser in player_data.get('inventory', {}).items():
                inv[item_id] = ItemStack.from_dict(ser)
            player_data['inventory_slots'] = _slots_from_legacy_inventory(inv)

        # Удаляем старый ключ инвентаря если он есть
        if 'inventory' in player_data:
            del player_data['inventory']

        return data  # Возвращаем загруженные данные
    except:
        return None  # Если файла нет или он повреждён - возвращаем None