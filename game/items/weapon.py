from game.items.tool import Tool

class Weapon(Tool):
    def __init__(self, item_id, name, description, durability, damage):
        super().__init__(item_id, name, description, durability, "weapon", power=damage)