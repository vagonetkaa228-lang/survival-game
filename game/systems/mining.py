"""Параметры добычи ресурсов и урон инструментов по животным."""

TREE_MAX_HP = 40
TREE_HAND_DAMAGE = 4       # 10 ударов голыми руками
TREE_AXE_DAMAGE = 10       # 4 ударов топором

STONE_MAX_HP = 50
STONE_PICKAXE_DAMAGE = 10  # 5 ударов киркой

AXE_ANIMAL_DAMAGE = 40
PICKAXE_ANIMAL_DAMAGE = 30


def can_mine_structure(structure_type, tool_item):
    if structure_type == "tree":
        return True
    if structure_type == "stone_vein":
        return tool_item is not None and getattr(tool_item, "tool_type", None) == "pickaxe"
    return False


def get_mining_damage(structure_type, tool_item):
    if structure_type == "tree":
        if tool_item and getattr(tool_item, "tool_type", None) == "axe":
            return TREE_AXE_DAMAGE
        return TREE_HAND_DAMAGE

    if structure_type == "stone_vein":
        if tool_item and getattr(tool_item, "tool_type", None) == "pickaxe":
            return STONE_PICKAXE_DAMAGE
        return 0

    return 0


def uses_tool_durability(structure_type, tool_item):
    if not tool_item or not hasattr(tool_item, "tool_type"):
        return False
    if structure_type == "tree" and tool_item.tool_type == "axe":
        return True
    if structure_type == "stone_vein" and tool_item.tool_type == "pickaxe":
        return True
    return False


def get_melee_tool_damage(tool_item):
    if not tool_item or not hasattr(tool_item, "tool_type"):
        return None
    if tool_item.tool_type == "axe":
        return AXE_ANIMAL_DAMAGE
    if tool_item.tool_type == "pickaxe":
        return PICKAXE_ANIMAL_DAMAGE
    return None
