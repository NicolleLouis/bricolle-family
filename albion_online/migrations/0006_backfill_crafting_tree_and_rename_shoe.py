from django.db import migrations


ARMOR_MATERIAL_BY_TOKEN = {
    "CLOTH": "cloth",
    "LEATHER": "leather",
    "PLATE": "metal",
}
ARMOR_SLOT_BY_TYPE = {
    "HEAD": "head",
    "ARMOR": "chest",
    "SHOES": "shoe",
}
WEAPON_PATTERNS = (
    ("SHAPESHIFTER", "shapeshifter_staff"),
    ("NATURESTAFF", "nature_staff"),
    ("WILDSTAFF", "nature_staff"),
    ("CURSEDSTAFF", "cursed_staff"),
    ("DEMONICSTAFF", "cursed_staff"),
    ("SKULLORB", "cursed_staff"),
    ("ARCANESTAFF", "arcane_staff"),
    ("ENIGMATICSTAFF", "arcane_staff"),
    ("ENIGMATICORB", "arcane_staff"),
    ("ARCANE", "arcane_staff"),
    ("HOLYSTAFF", "holy_staff"),
    ("DIVINESTAFF", "holy_staff"),
    ("FIRESTAFF", "fire_staff"),
    ("INFERNOSTAFF", "fire_staff"),
    ("FIRE", "fire_staff"),
    ("FROSTSTAFF", "frost_staff"),
    ("GLACIALSTAFF", "frost_staff"),
    ("ICEGAUNTLETS", "frost_staff"),
    ("ICECRYSTAL", "frost_staff"),
    ("QUARTERSTAFF", "quarterstaff"),
    ("DOUBLEBLADEDSTAFF", "quarterstaff"),
    ("IRONCLADEDSTAFF", "quarterstaff"),
    ("COMBATSTAFF", "quarterstaff"),
    ("ROCKSTAFF", "quarterstaff"),
    ("KNUCKLES", "knuckles"),
    ("GAUNTLETS", "knuckles"),
    ("CROSSBOW", "crossbow"),
    ("BOW", "bow"),
    ("DAGGER", "dagger"),
    ("CLAW", "dagger"),
    ("SICKLE", "dagger"),
    ("KATAR", "dagger"),
    ("SPEAR", "spear"),
    ("GLAIVE", "spear"),
    ("HARPOON", "spear"),
    ("TRIDENT", "spear"),
    ("AXE", "axe"),
    ("SCYTHE", "axe"),
    ("CLEAVER", "axe"),
    ("SWORD", "sword"),
    ("CLAYMORE", "sword"),
    ("SCIMITAR", "sword"),
    ("RAPIER", "sword"),
    ("MACE", "mace"),
    ("FLAIL", "mace"),
    ("HAMMER", "hammer"),
    ("RAM", "hammer"),
)
OFFHAND_PATTERNS = (
    ("SHIELD", "shield"),
    ("TOTEM", "shield"),
    ("BOOK", "book"),
    ("TOME", "book"),
    ("LAMP", "book"),
    ("ORB", "orb"),
    ("SKULL", "orb"),
    ("TORCH", "torch"),
    ("CENSER", "censer"),
    ("HORN", "horn"),
    ("TALISMAN", "talisman"),
    ("JESTERCANE", "talisman"),
)


def resolve_from_patterns(payload, patterns):
    for pattern, crafting_tree in patterns:
        if pattern in payload:
            return crafting_tree
    return None


def resolve_crafting_tree(aodp_id):
    normalized_aodp_id = aodp_id.split("@", 1)[0]
    parts = normalized_aodp_id.split("_")
    if len(parts) < 2:
        return None

    if parts[0].startswith("T") and parts[0][1:].isdigit():
        object_type = parts[1]
        object_payload = "_".join(parts[2:])
    else:
        object_type = parts[0]
        object_payload = "_".join(parts[1:])

    if object_type in ARMOR_SLOT_BY_TYPE:
        slot = ARMOR_SLOT_BY_TYPE[object_type]
        if len(parts) < 3:
            return None
        material_token = parts[2]
        material = ARMOR_MATERIAL_BY_TOKEN.get(material_token)
        if material is not None:
            return f"{material}_{slot}"
        if material_token == "GATHERER" and len(parts) >= 4:
            return f"gatherer_{parts[3].lower()}_{slot}"
        return None

    if object_type in {"MAIN", "2H"}:
        return resolve_from_patterns(object_payload, WEAPON_PATTERNS)
    if object_type == "OFF":
        return resolve_from_patterns(object_payload, OFFHAND_PATTERNS)
    return None


def backfill_crafting_tree_and_rename_shoe(apps, schema_editor):
    Object = apps.get_model("albion_online", "Object")
    Object.objects.filter(equipment_category="BOOT").update(equipment_category="SHOE")

    objects_to_update = []
    for albion_object in Object.objects.all().only("id", "aodp_id", "crafting_tree"):
        crafting_tree = resolve_crafting_tree(albion_object.aodp_id)
        if albion_object.crafting_tree != crafting_tree:
            albion_object.crafting_tree = crafting_tree
            objects_to_update.append(albion_object)

    Object.objects.bulk_update(objects_to_update, ["crafting_tree"], batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ("albion_online", "0005_alter_object_options_object_crafting_tree_and_more"),
    ]

    operations = [
        migrations.RunPython(
            backfill_crafting_tree_and_rename_shoe,
            migrations.RunPython.noop,
        ),
    ]
