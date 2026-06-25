from game.items.consumable import Food
from game.items.consumable import Water

from game.items.resource import Resource
from game.items.tool import Tool

ITEMS = {}

def register_item(item):
    ITEMS[item.id] = item


register_item(Food("berry", "Ягоды", hunger_restore=5))
register_item(Food("meat", "Мясо", hunger_restore=15, health_restore=5))
register_item(Water("clean_water", "Чистая вода", thirst_restore=20))

register_item(Resource("wood", "Дерево"))
register_item(Resource("stone", "Камень"))
register_item(Resource("fiber", "Волокно"))
register_item(Resource("campfire", "Костёр"))
register_item(Resource("torch", "Факел"))
register_item(Resource("bandage", "Бинт"))

register_item(Resource("campfire_kit", "Набор для костра"))
register_item(Resource("wood_wall_kit", "Деревянная стена"))
register_item(Resource("wood_door_kit", "Деревянная дверь"))



register_item(Tool("stone_axe", "Каменный топор", "Простой топор", durability=30, tool_type="axe", power=40))
register_item(Tool("stone_pickaxe", "Каменная кирка", "Простая кирка", durability=30, tool_type="pickaxe", power=30))

register_item(Tool("spear", "Копьё", "Увеличивает дальность атаки", durability=40, tool_type="spear", power=10))
register_item(Tool("bow", "Лук", "Стрельба стрелами", durability=30, tool_type="bow", power=5))
register_item(Resource("arrow", "Стрела", "Боеприпас для лука"))
# Пистолет – не крафтится, появляется в мире
register_item(Tool("pistol", "Пистолет", "Огнестрел, 8 патронов", durability=8, tool_type="gun", power=30))
register_item(Resource("magazine", "Магазин", "Патроны для пистолета"))
register_item(Resource("raft", "Плот", "Плот для побега с острова"))