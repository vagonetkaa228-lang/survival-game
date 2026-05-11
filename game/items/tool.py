from game.items.item import Item

class Tool(Item):
    def __init__(self, item_id, name, description, durability, tool_type, power=1):
        super().__init__(item_id, name, description, max_stack=1)
        self.durability = durability
        self.max_durability = durability
        self.tool_type = tool_type  # "axe" или "pickaxe"
        self.power = power          # урон по структуре

    def use(self, player):
        # Инструменты не расходуются при использовании, только при добыче
        return False