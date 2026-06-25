
from game.items.registry import ITEMS

class ItemStack:
    """Экземпляр предмета в инвентаре: id, количество и прочность (для инструментов)"""
    def __init__(self, item_id, count=1, durability=None):
        self.item_id = item_id
        self.count = count
        # Если прочность не задана, берём из прототипа (для Tool)
        if durability is None:
            prototype = ITEMS.get(item_id)
            if prototype and hasattr(prototype, 'max_durability'):
                self.durability = prototype.max_durability
            else:
                self.durability = None
        else:
            self.durability = durability

    @property
    def is_tool(self):
        return self.durability is not None

    def to_dict(self):
        """Сериализация для сохранения"""
        return {
            'item_id': self.item_id,
            'count': self.count,
            'durability': self.durability
        }

    @staticmethod
    def from_dict(data):
        return ItemStack(data['item_id'], data['count'], data.get('durability'))