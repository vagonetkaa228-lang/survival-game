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

STORY_RECIPES = {
    "raft": Recipe("raft", 1, {"wood": 15, "stone": 10}),
}


def get_recipes_for_player(unlocked_story_ids=None):
    recipes = list(RECIPES)
    if unlocked_story_ids:
        for recipe_id in unlocked_story_ids:
            if recipe_id in STORY_RECIPES:
                recipes.append(STORY_RECIPES[recipe_id])
    return recipes