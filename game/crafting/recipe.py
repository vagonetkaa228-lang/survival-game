class Recipe:
    def __init__(self, result_item_id, result_amount, ingredients):

        self.result_item_id = result_item_id  # ID предмета, который получается
        self.result_amount = result_amount    # Количество получаемого предмета
        self.ingredients = ingredients        # Словарь требуемых ингредиентов

    def can_craft(self, player):
        """Проверяет, хватает ли у игрока ресурсов для крафта"""
        for item_id, amount in self.ingredients.items():  # Перебираем все ингредиенты
            if player.count_item(item_id) < amount:       # Если игрок имеет меньше чем нужно
                return False                               # Не хватает - нельзя скрафтить
        return True                                        # Всех ресурсов достаточно

    def craft(self, player):
        """Выполняет крафт: забирает ингредиенты и даёт результат"""
        if not self.can_craft(player):     # Если не хватает ресурсов
            return None                    # Ничего не делаем

        # Забираем ингредиенты из инвентаря игрока
        for item_id, amount in self.ingredients.items():
            player.remove_item(item_id, amount)   # Удаляем каждый ингредиент

        # Добавляем результат крафта в инвентарь игрока
        player.add_item(self.result_item_id, self.result_amount)

        return self.result_item_id         # Возвращаем ID созданного предмета