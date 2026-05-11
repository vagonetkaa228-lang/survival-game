from game.items.item import Item

class Resource(Item):
    def __init__(self, item_id, name, description=""):
        super().__init__(item_id, name, description)
        # Ресурсы нельзя использовать напрямую, только для крафта