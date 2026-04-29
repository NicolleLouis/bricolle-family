LEATHER_JACKET_TYPES = (
    {
        "key": "mercenary",
        "label": "Mercenary",
        "recipe_key": "mercenary_jacket",
        "recipe_name": "Mercenary Jacket recipes",
        "aodp_id_fragment": "ARMOR_LEATHER_SET1",
    },
    {
        "key": "hunter",
        "label": "Hunter",
        "recipe_key": "hunter_jacket",
        "recipe_name": "Hunter Jacket recipes",
        "aodp_id_fragment": "ARMOR_LEATHER_SET2",
    },
    {
        "key": "assassin",
        "label": "Assassin",
        "recipe_key": "assassin_jacket",
        "recipe_name": "Assassin Jacket recipes",
        "aodp_id_fragment": "ARMOR_LEATHER_SET3",
    },
)

LEATHER_JACKET_TYPE_BY_KEY = {jacket_type["key"]: jacket_type for jacket_type in LEATHER_JACKET_TYPES}
