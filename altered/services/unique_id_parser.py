from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ParsedUniqueId:
    extension_code: str
    art_letter: str
    faction_code: str
    faction_value: str
    faction_name: str
    card_number: int
    card_number_segment: str
    rarity_code: str
    rarity_name: str
    is_unique: bool
    unique_instance_id: Optional[int]


class UniqueIdParserService:
    FACTION_CODES = {
        "AX": ("AXIOM", "Axiom"),
        "BR": ("BRAVOS", "Bravos"),
        "LY": ("LYRA", "Lyra"),
        "MU": ("MUNA", "Muna"),
        "OR": ("ORDIS", "Ordis"),
        "YZ": ("YZMIR", "Yzmir"),
    }

    RARITY_CODES = {
        "C": ("Common", False),
        "R1": ("Rare", False),
        "U": ("Unique", True),
        "R2": ("Rare Transfuge", False),
    }

    EXPECTED_PREFIX = "ALT"

    @classmethod
    def parse(cls, card_id: str) -> ParsedUniqueId:
        parts = card_id.split("_")

        if len(parts) not in (6, 7):
            raise ValueError("card_id must contain either 6 or 7 segments separated by underscores.")

        prefix, extension_code, art_letter, faction_code, card_number_segment, rarity_code, *rest = parts

        if prefix != cls.EXPECTED_PREFIX:
            raise ValueError(f"card_id must start with '{cls.EXPECTED_PREFIX}'.")

        faction_info = cls.FACTION_CODES.get(faction_code)
        if faction_info is None:
            raise ValueError(f"Unknown faction code '{faction_code}'.")

        rarity_info = cls.RARITY_CODES.get(rarity_code)
        if rarity_info is None:
            raise ValueError(f"Unknown rarity code '{rarity_code}'.")

        faction_value, faction_display = faction_info
        rarity_name, is_unique = rarity_info

        unique_instance_id = None
        if rest:
            if not is_unique:
                raise ValueError("Only unique cards can have an instance identifier.")
            unique_instance_id = cls._parse_integer(rest[0], "unique identifier")

        card_number_int = cls._parse_integer(card_number_segment, "card number")

        return ParsedUniqueId(
            extension_code=extension_code,
            art_letter=art_letter,
            faction_code=faction_code,
            faction_value=faction_value,
            faction_name=faction_display,
            card_number=card_number_int,
            card_number_segment=card_number_segment,
            rarity_code=rarity_code,
            rarity_name=rarity_name,
            is_unique=is_unique,
            unique_instance_id=unique_instance_id,
        )

    @staticmethod
    def _parse_integer(value: str, field_name: str) -> int:
        try:
            return int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Unable to parse {field_name} as integer.") from exc
