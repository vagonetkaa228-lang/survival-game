class Item:
    def __init__(self, item_id, name, description, max_stack=99, icon=None):
        self.id = item_id
        self.name = name
        self.description = description
        self.max_stack = max_stack
        self.icon = icon

    def use(self, player):
        """Вызывается при использовании предмета (например, съесть)"""
        pass