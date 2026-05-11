from game.crafting.recipe import Recipe

RECIPES = [
    Recipe("campfire_kit", 1, {"wood": 5, "stone": 3}),
    Recipe("wood_wall_kit", 1, {"wood": 10}),
    Recipe("wood_door_kit", 1, {"wood": 8}),
    Recipe("stone_axe", 1, {"wood": 3, "stone": 2}),
    Recipe("stone_pickaxe", 1, {"wood": 2, "stone": 3}),
    Recipe("spear", 1, {"wood": 3, "stone": 2}),
    Recipe("bow", 1, {"wood": 4, "stone": 2}),
    Recipe("arrow", 3, {"wood": 2, "stone": 1}),
]