from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType


GATHERING_GEAR_DEFAULT_CITY_FILTER = City.FORT_STERLING
GATHERING_GEAR_DEFAULT_RESOURCE_FILTER = "ore"

_GATHERING_GEAR_SLOT_DEFINITIONS = (
    {
        "key": "head",
        "label": "Cap",
        "object_type": ObjectType.HEAD,
        "crafting_tree_slot": "head",
    },
    {
        "key": "chest",
        "label": "Garb",
        "object_type": ObjectType.ARMOR,
        "crafting_tree_slot": "chest",
    },
    {
        "key": "shoe",
        "label": "Workboot",
        "object_type": ObjectType.SHOES,
        "crafting_tree_slot": "shoe",
    },
)

GATHERING_GEAR_RESOURCE_GROUPS = (
    {
        "key": "ore",
        "label": "Ore",
        "recipe_key_prefix": "miner",
        "item_prefix": "Miner",
        "aodp_id_fragment": "GATHERER_ORE",
        "main_input_type": ObjectType.METALBAR,
    },
    {
        "key": "fiber",
        "label": "Fiber",
        "recipe_key_prefix": "harvester",
        "item_prefix": "Harvester",
        "aodp_id_fragment": "GATHERER_FIBER",
        "main_input_type": ObjectType.ORE,
    },
    {
        "key": "wood",
        "label": "Wood",
        "recipe_key_prefix": "lumberjack",
        "item_prefix": "Lumberjack",
        "aodp_id_fragment": "GATHERER_WOOD",
        "main_input_type": ObjectType.ORE,
    },
    {
        "key": "stone",
        "label": "Stone",
        "recipe_key_prefix": "quarrier",
        "item_prefix": "Quarrier",
        "aodp_id_fragment": "GATHERER_ROCK",
        "main_input_type": ObjectType.ORE,
    },
    {
        "key": "hide",
        "label": "Hide",
        "recipe_key_prefix": "skinner",
        "item_prefix": "Skinner",
        "aodp_id_fragment": "GATHERER_HIDE",
        "main_input_type": ObjectType.ORE,
    },
)

GATHERING_GEAR_RESOURCE_GROUPS_BY_KEY = {
    resource_group["key"]: resource_group for resource_group in GATHERING_GEAR_RESOURCE_GROUPS
}

GATHERING_GEAR_RESOURCE_FILTER_OPTIONS = (
    *[
        {"value": resource_group["key"], "label": resource_group["label"]}
        for resource_group in GATHERING_GEAR_RESOURCE_GROUPS
    ],
)

GATHERING_GEAR_VARIANT_COLUMNS = (
    {
        "key": "head",
        "label": "Cap",
        "object_type": ObjectType.HEAD,
    },
    {
        "key": "armor",
        "label": "Garb",
        "object_type": ObjectType.ARMOR,
    },
    {
        "key": "shoe",
        "label": "Workboot",
        "object_type": ObjectType.SHOES,
    },
    {
        "key": "backpack",
        "label": "Backpack",
        "object_type": ObjectType.BACKPACK,
    },
)

GATHERING_GEAR_VARIANT_COLUMNS_BY_OBJECT_TYPE = {
    variant_column["object_type"]: variant_column for variant_column in GATHERING_GEAR_VARIANT_COLUMNS
}


def _build_standard_recipe_definition(resource_group, slot_definition):
    return {
        "key": f"{resource_group['recipe_key_prefix']}_{slot_definition['key']}",
        "name": f"{resource_group['item_prefix']} {slot_definition['label']} recipes",
        "config": {
            "output_filter": {
                "aodp_id__contains": resource_group["aodp_id_fragment"],
                "type": slot_definition["object_type"],
                "crafting_tree": f"gatherer_{resource_group['key']}_{slot_definition['crafting_tree_slot']}",
                "tier__gte": 4,
            },
            "output_quantity": 1,
            "inputs": [
                {
                    "object_filter": {
                        "type": resource_group["main_input_type"],
                    },
                    "tier_mode": "same_as_output",
                    "enchantment_mode": "same_as_output",
                    "quantity": 8,
                }
            ],
        },
    }


def _build_backpack_recipe_definition(resource_group):
    return {
        "key": f"{resource_group['recipe_key_prefix']}_backpack",
        "name": f"{resource_group['item_prefix']} Backpack recipes",
        "config": {
            "output_filter": {
                "aodp_id__contains": resource_group["aodp_id_fragment"],
                "type": ObjectType.BACKPACK,
                "tier__gte": 4,
            },
            "output_quantity": 1,
            "inputs": [
                {
                    "object_filter": {
                        "type": ObjectType.CLOTH,
                    },
                    "tier_mode": "same_as_output",
                    "enchantment_mode": "same_as_output",
                    "quantity": 4,
                },
                {
                    "object_filter": {
                        "type": ObjectType.LEATHER,
                    },
                    "tier_mode": "same_as_output",
                    "enchantment_mode": "same_as_output",
                    "quantity": 4,
                },
            ],
        },
    }


def _build_resource_recipe_definitions(resource_group):
    return (
        *[
            _build_standard_recipe_definition(resource_group, slot_definition)
            for slot_definition in _GATHERING_GEAR_SLOT_DEFINITIONS
        ],
        _build_backpack_recipe_definition(resource_group),
    )


GATHERING_GEAR_RECIPE_DEFINITIONS = tuple(
    recipe_definition
    for resource_group in GATHERING_GEAR_RESOURCE_GROUPS
    for recipe_definition in _build_resource_recipe_definitions(resource_group)
)
