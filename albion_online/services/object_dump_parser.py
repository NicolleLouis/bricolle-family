import re
from dataclasses import dataclass

from albion_online.services.crafting_tree_resolver import CraftingTreeResolver
from albion_online.services.equipment_category_resolver import EquipmentCategoryResolver


@dataclass(frozen=True)
class ParsedObject:
    aodp_id: str
    name: str
    type: str
    tier: int | None
    enchantment: int
    tier_enchantment_notation: str | None
    equipment_category: str | None
    crafting_tree: str | None


class ObjectDumpParser:
    _line_pattern = re.compile(
        r"^\s*\d+:\s+(?P<aodp_id>\S+)(?:\s*:\s*(?P<name>.*))?\s*$"
    )
    _tier_pattern = re.compile(r"^T(?P<tier>[1-8])_(?P<type_payload>.+)$")
    _enchantment_pattern = re.compile(r"^(?P<base_aodp_id>.+)@(?P<enchantment>[0-4])$")

    def __init__(self):
        self._crafting_tree_resolver = CraftingTreeResolver()
        self._equipment_category_resolver = EquipmentCategoryResolver()

    def parse(self, content: str) -> list[ParsedObject]:
        parsed_objects = []
        for line in content.splitlines():
            parsed_object = self._parse_line(line)
            if parsed_object is not None:
                parsed_objects.append(parsed_object)
        return parsed_objects

    def _parse_line(self, line: str) -> ParsedObject | None:
        line_match = self._line_pattern.match(line)
        if line_match is None:
            return None

        aodp_id = line_match.group("aodp_id")
        name = (line_match.group("name") or "").strip()
        base_aodp_id, enchantment = self._split_enchantment(aodp_id)
        tier, type_payload = self._split_tier(base_aodp_id)
        object_type = type_payload.split("_", 1)[0]

        return ParsedObject(
            aodp_id=aodp_id,
            name=name,
            type=object_type,
            tier=tier,
            enchantment=enchantment,
            tier_enchantment_notation=self._build_tier_enchantment_notation(
                tier,
                enchantment,
            ),
            equipment_category=self._equipment_category_resolver.resolve(object_type),
            crafting_tree=self._crafting_tree_resolver.resolve(aodp_id),
        )

    def _build_tier_enchantment_notation(self, tier: int | None, enchantment: int) -> str | None:
        if tier is None:
            return None
        return f"{tier}.{enchantment}"

    def _split_enchantment(self, aodp_id: str) -> tuple[str, int]:
        enchantment_match = self._enchantment_pattern.match(aodp_id)
        if enchantment_match is None:
            return aodp_id, 0
        return (
            enchantment_match.group("base_aodp_id"),
            int(enchantment_match.group("enchantment")),
        )

    def _split_tier(self, base_aodp_id: str) -> tuple[int | None, str]:
        tier_match = self._tier_pattern.match(base_aodp_id)
        if tier_match is None:
            return None, base_aodp_id
        return int(tier_match.group("tier")), tier_match.group("type_payload")
