

class Recipe:
    def __init__(self, result_item_id, result_amount, ingredients):
        """
        ingredients - словарь {item_id: количество}
        """
        self.result_item_id = result_item_id
        self.result_amount = result_amount
        self.ingredients = ingredients

    def can_craft(self, player):
        for item_id, amount in self.ingredients.items():
            if player.count_item(item_id) < amount:
                return False
        return True
    def craft(self, player):
        if not self.can_craft(player):
            return None
        for item_id, amount in self.ingredients.items():
            player.remove_item(item_id, amount)
        player.add_item(self.result_item_id, self.result_amount)
        return self.result_item_id