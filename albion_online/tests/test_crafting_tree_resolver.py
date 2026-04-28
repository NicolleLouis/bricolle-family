from albion_online.services.crafting_tree_resolver import CraftingTreeResolver


class TestCraftingTreeResolver:
    def test_resolve_armor_material_and_slot(self):
        resolver = CraftingTreeResolver()

        assert resolver.resolve("T4_HEAD_CLOTH_SET1") == "cloth_head"
        assert resolver.resolve("T4_ARMOR_LEATHER_SET1") == "leather_chest"
        assert resolver.resolve("T4_SHOES_PLATE_SET1") == "metal_shoe"

    def test_resolve_gatherer_armor(self):
        resolver = CraftingTreeResolver()

        assert resolver.resolve("T4_HEAD_GATHERER_FIBER") == "gatherer_fiber_head"
        assert resolver.resolve("T4_ARMOR_GATHERER_FISH") == "gatherer_fish_chest"
        assert resolver.resolve("T4_SHOES_GATHERER_ORE") == "gatherer_ore_shoe"

    def test_resolve_weapon_families(self):
        resolver = CraftingTreeResolver()

        assert resolver.resolve("T4_MAIN_AXE") == "axe"
        assert resolver.resolve("T4_2H_BOW") == "bow"
        assert resolver.resolve("T4_2H_WILDSTAFF") == "nature_staff"
        assert resolver.resolve("T4_2H_SKULLORB_HELL") == "cursed_staff"

    def test_resolve_offhand_families(self):
        resolver = CraftingTreeResolver()

        assert resolver.resolve("T4_OFF_SHIELD") == "shield"
        assert resolver.resolve("T4_OFF_TOME_CRYSTAL") == "book"
        assert resolver.resolve("T4_OFF_JESTERCANE_HELL") == "talisman"

    def test_resolve_non_equipment_object(self):
        assert CraftingTreeResolver().resolve("T2_POTION_HEAL@1") is None
