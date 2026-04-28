from albion_online.services.equipment_category_resolver import EquipmentCategoryResolver


class TestEquipmentCategoryResolver:
    def test_resolve_equipment_types(self):
        resolver = EquipmentCategoryResolver()

        assert resolver.resolve("ARMOR") == "CHEST"
        assert resolver.resolve("OFF") == "OFFHAND"
        assert resolver.resolve("MAIN") == "SINGLE_HAND"
        assert resolver.resolve("2H") == "TWO_HAND"
        assert resolver.resolve("SHOES") == "SHOE"

    def test_resolve_non_equipment_type(self):
        assert EquipmentCategoryResolver().resolve("POTION") is None
