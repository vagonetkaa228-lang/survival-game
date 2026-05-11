from game.items.item import Item

class Food(Item):
    def __init__(self, item_id, name, hunger_restore, health_restore=0):
        super().__init__(item_id, name, f"Восстанавливает {hunger_restore} голода")
        self.hunger_restore = hunger_restore
        self.health_restore = health_restore

    def use(self, player):
        player.hunger = min(100, player.hunger + self.hunger_restore)
        player.health = min(100, player.health + self.health_restore)
        return True  # предмет израсходован

class Water(Item):
    def __init__(self, item_id, name, thirst_restore, health_restore=0):
        super().__init__(item_id, name, f"Восстанавливает {thirst_restore} жажды")
        self.thirst_restore = thirst_restore
        self.health_restore = health_restore

    def use(self, player):
        player.thirst = min(100, player.thirst + self.thirst_restore)
        player.health = min(100, player.health + self.health_restore)
        return True