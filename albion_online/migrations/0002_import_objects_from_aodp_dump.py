import re
from urllib.request import urlopen

from django.db import migrations


SOURCE_URL = "https://raw.githubusercontent.com/ao-data/ao-bin-dumps/master/formatted/items.txt"
LINE_PATTERN = re.compile(
    r"^\s*\d+:\s+(?P<aodp_id>\S+)(?:\s*:\s*(?P<name>.*))?\s*$"
)
TIER_PATTERN = re.compile(r"^T(?P<tier>[1-8])_(?P<type_payload>.+)$")
ENCHANTMENT_PATTERN = re.compile(
    r"^(?P<base_aodp_id>.+)@(?P<enchantment>[0-4])$"
)


def split_enchantment(aodp_id):
    enchantment_match = ENCHANTMENT_PATTERN.match(aodp_id)
    if enchantment_match is None:
        return aodp_id, 0
    return (
        enchantment_match.group("base_aodp_id"),
        int(enchantment_match.group("enchantment")),
    )


def split_tier(base_aodp_id):
    tier_match = TIER_PATTERN.match(base_aodp_id)
    if tier_match is None:
        return None, base_aodp_id
    return int(tier_match.group("tier")), tier_match.group("type_payload")


def parse_object_line(line):
    line_match = LINE_PATTERN.match(line)
    if line_match is None:
        return None

    aodp_id = line_match.group("aodp_id")
    name = (line_match.group("name") or "").strip()
    base_aodp_id, enchantment = split_enchantment(aodp_id)
    tier, type_payload = split_tier(base_aodp_id)

    return {
        "aodp_id": aodp_id,
        "name": name,
        "type": type_payload.split("_", 1)[0],
        "tier": tier,
        "enchantment": enchantment,
    }


def fetch_source_content():
    with urlopen(SOURCE_URL, timeout=30) as response:
        return response.read().decode("utf-8")


def import_objects_from_aodp_dump(apps, schema_editor):
    Object = apps.get_model("albion_online", "Object")
    source_content = fetch_source_content()
    objects = []

    for line in source_content.splitlines():
        parsed_object = parse_object_line(line)
        if parsed_object is None:
            continue
        objects.append(Object(**parsed_object))

    Object.objects.bulk_create(objects, ignore_conflicts=True, batch_size=500)


class Migration(migrations.Migration):

    dependencies = [
        ("albion_online", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(import_objects_from_aodp_dump, migrations.RunPython.noop),
    ]
