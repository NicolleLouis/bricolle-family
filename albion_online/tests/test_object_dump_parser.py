from albion_online.services.object_dump_parser import ObjectDumpParser


class TestObjectDumpParser:
    def test_parse_tiered_object_without_enchantment(self):
        parsed_objects = ObjectDumpParser().parse(
            "   2: T3_2H_TOOL_TRACKING                                              : Journeyman's Tracking Toolkit"
        )

        assert len(parsed_objects) == 1
        parsed_object = parsed_objects[0]
        assert parsed_object.aodp_id == "T3_2H_TOOL_TRACKING"
        assert parsed_object.name == "Journeyman's Tracking Toolkit"
        assert parsed_object.type == "2H"
        assert parsed_object.tier == 3
        assert parsed_object.enchantment == 0
        assert parsed_object.tier_enchantment_notation == "3.0"
        assert parsed_object.equipment_category == "TWO_HAND"
        assert parsed_object.crafting_tree is None

    def test_parse_tiered_object_with_enchantment(self):
        parsed_objects = ObjectDumpParser().parse(
            " 531: T2_POTION_HEAL@1                                                 : Minor Healing Potion"
        )

        assert len(parsed_objects) == 1
        parsed_object = parsed_objects[0]
        assert parsed_object.aodp_id == "T2_POTION_HEAL@1"
        assert parsed_object.name == "Minor Healing Potion"
        assert parsed_object.type == "POTION"
        assert parsed_object.tier == 2
        assert parsed_object.enchantment == 1
        assert parsed_object.tier_enchantment_notation == "2.1"
        assert parsed_object.equipment_category is None
        assert parsed_object.crafting_tree is None

    def test_parse_non_tiered_object(self):
        parsed_objects = ObjectDumpParser().parse(
            "   1: UNIQUE_HIDEOUT                                                   : Hideout Construction Kit"
        )

        assert len(parsed_objects) == 1
        parsed_object = parsed_objects[0]
        assert parsed_object.aodp_id == "UNIQUE_HIDEOUT"
        assert parsed_object.name == "Hideout Construction Kit"
        assert parsed_object.type == "UNIQUE"
        assert parsed_object.tier is None
        assert parsed_object.enchantment == 0
        assert parsed_object.tier_enchantment_notation is None
        assert parsed_object.equipment_category is None
        assert parsed_object.crafting_tree is None

    def test_parse_object_without_name(self):
        parsed_objects = ObjectDumpParser().parse(
            " 504: T8_CONSUMABLE_SPECIAL_NONTRADABLE@1                              "
        )

        assert len(parsed_objects) == 1
        parsed_object = parsed_objects[0]
        assert parsed_object.aodp_id == "T8_CONSUMABLE_SPECIAL_NONTRADABLE@1"
        assert parsed_object.name == ""
        assert parsed_object.type == "CONSUMABLE"
        assert parsed_object.tier == 8
        assert parsed_object.enchantment == 1
        assert parsed_object.tier_enchantment_notation == "8.1"
        assert parsed_object.equipment_category is None
        assert parsed_object.crafting_tree is None
