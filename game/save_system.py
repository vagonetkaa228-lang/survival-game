import json
from game.items.item_stack import ItemStack

SAVE_FILE = 'save.json'

def save_game(player):
    ser_inv = {}
    for item_id, stack in player.inventory.items():
        ser_inv[item_id] = stack.to_dict()
    data = {
        'player': {
            'x': player.x,
            'y': player.y,
            'health': player.health,
            'hunger': player.hunger,
            'thirst': player.thirst,
            'energy': player.energy,
            'inventory': ser_inv,
            'hotbar': player.hotbar,
            'active_item_id': player.active_item_id
        }
    }
    with open(SAVE_FILE, 'w') as f:
        json.dump(data, f)

def load_game():
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
        player_data = data['player']
        # Восстанавливаем инвентарь как ItemStack
        inv = {}
        for item_id, ser in player_data['inventory'].items():
            inv[item_id] = ItemStack.from_dict(ser)
        player_data['inventory'] = inv
        # Остальные поля можно передать в конструктор Player через __dict__
        return data
    except:
        return None


