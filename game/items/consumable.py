from game.items.item import Item

class Food(Item):
    def __init__(self, item_id, name, hunger_restore, health_restore=0):
        super().__init__(item_id, name, f"Восстанавливает {hunger_restore} голода") # вызываем конструктор базового класса
        self.hunger_restore = hunger_restore # сколько восстанавливает голода
        self.health_restore = health_restore # сколько восстанавливает здоровья (опционально)

    def use(self, player):
        player.hunger = min(100, player.hunger + self.hunger_restore) # увеличиваем сытость, не выше 100
        player.health = min(100, player.health + self.health_restore) # увеличиваем здоровье, не выше 100
        return True # предмет израсходован (удаляется из инвентаря)

class Water(Item):
    def __init__(self, item_id, name, thirst_restore, health_restore=0):
        super().__init__(item_id, name, f"Восстанавливает {thirst_restore} жажды") # конструктор базового класса
        self.thirst_restore = thirst_restore # сколько восстанавливает жажды
        self.health_restore = health_restore # сколько восстанавливает здоровья (опционально)

    def use(self, player):
        player.thirst = min(100, player.thirst + self.thirst_restore) # увеличиваем утоление жажды, не выше 100
        player.health = min(100, player.health + self.health_restore) # увеличиваем здоровье, не выше 100
        return True # предмет израсходован