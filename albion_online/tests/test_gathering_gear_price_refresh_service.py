import pytest

from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Recipe, RecipeInput
from albion_online.services.gathering_gear_price_refresh import (
    GatheringGearPriceRefreshService,
)


class FakeFetcher:
    def __init__(self):
        self.requested_objects_batches = []

    def fetch_current_prices(self, objects):
        self.requested_objects_batches.append(list(objects))
        return []


@pytest.mark.django_db
class TestGatheringGearPriceRefreshService:
    def test_refresh_prices_fetches_all_resource_groups_and_recipe_inputs(self):
        fetcher = FakeFetcher()
        miner_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_ORE_REFRESH",
            name="Adept's Miner Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_ore_head",
        )
        miner_garb = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_GATHERER_ORE_REFRESH",
            name="Adept's Miner Garb",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="gatherer_ore_chest",
        )
        miner_workboot = Object.objects.create(
            aodp_id="TEST_T4_SHOES_GATHERER_ORE_REFRESH",
            name="Adept's Miner Workboot",
            type_id=ObjectType.SHOES,
            tier=4,
            enchantment=2,
            equipment_category="SHOE",
            crafting_tree="gatherer_ore_shoe",
        )
        miner_backpack = Object.objects.create(
            aodp_id="TEST_T4_BACKPACK_GATHERER_ORE_REFRESH",
            name="Adept's Miner Backpack",
            type_id=ObjectType.BACKPACK,
            tier=4,
            enchantment=0,
        )
        fiber_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_FIBER_REFRESH",
            name="Adept's Harvester Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_fiber_head",
        )
        metalbar = Object.objects.create(
            aodp_id="TEST_T4_METALBAR_REFRESH@2",
            name="Adept's Metal Bar",
            type_id=ObjectType.METALBAR,
            tier=4,
            enchantment=2,
        )
        cloth = Object.objects.create(
            aodp_id="TEST_T4_CLOTH_REFRESH@2",
            name="Adept's Cloth",
            type_id=ObjectType.CLOTH,
            tier=4,
            enchantment=2,
        )
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_REFRESH@2",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=2,
        )
        wood = Object.objects.create(
            aodp_id="TEST_T4_WOOD_REFRESH@2",
            name="Adept's Wood",
            type_id=ObjectType.ORE,
            tier=4,
            enchantment=2,
        )
        stone = Object.objects.create(
            aodp_id="TEST_T4_ROCK_REFRESH@2",
            name="Adept's Stone",
            type_id=ObjectType.ORE,
            tier=4,
            enchantment=2,
        )
        hide = Object.objects.create(
            aodp_id="TEST_T4_HIDE_REFRESH@2",
            name="Adept's Hide",
            type_id=ObjectType.ORE,
            tier=4,
            enchantment=2,
        )
        ore = Object.objects.create(
            aodp_id="TEST_T4_ORE_REFRESH@2",
            name="Adept's Ore",
            type_id=ObjectType.ORE,
            tier=4,
            enchantment=2,
        )

        miner_cap_recipe = Recipe.objects.create(output=miner_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=miner_cap_recipe, object=metalbar, quantity=8)
        miner_garb_recipe = Recipe.objects.create(output=miner_garb, output_quantity=1)
        RecipeInput.objects.create(recipe=miner_garb_recipe, object=metalbar, quantity=8)
        miner_workboot_recipe = Recipe.objects.create(output=miner_workboot, output_quantity=1)
        RecipeInput.objects.create(recipe=miner_workboot_recipe, object=metalbar, quantity=8)
        miner_backpack_recipe = Recipe.objects.create(output=miner_backpack, output_quantity=1)
        RecipeInput.objects.create(recipe=miner_backpack_recipe, object=cloth, quantity=4)
        RecipeInput.objects.create(recipe=miner_backpack_recipe, object=leather, quantity=4)
        fiber_cap_recipe = Recipe.objects.create(output=fiber_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=fiber_cap_recipe, object=ore, quantity=8)
        wood_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_WOOD_REFRESH",
            name="Adept's Lumberjack Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_wood_head",
        )
        stone_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_ROCK_REFRESH",
            name="Adept's Quarrier Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_rock_head",
        )
        hide_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_HIDE_REFRESH",
            name="Adept's Skinner Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_hide_head",
        )
        fish_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_FISH_REFRESH",
            name="Adept's Fisherman Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_fish_head",
        )
        fish_garb = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_GATHERER_FISH_REFRESH",
            name="Adept's Fisherman Garb",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="gatherer_fish_chest",
        )
        fish_workboot = Object.objects.create(
            aodp_id="TEST_T4_SHOES_GATHERER_FISH_REFRESH",
            name="Adept's Fisherman Workboots",
            type_id=ObjectType.SHOES,
            tier=4,
            enchantment=2,
            equipment_category="SHOE",
            crafting_tree="gatherer_fish_shoe",
        )
        fish_backpack = Object.objects.create(
            aodp_id="TEST_T4_BACKPACK_GATHERER_FISH_REFRESH",
            name="Adept's Fisherman Backpack",
            type_id=ObjectType.BACKPACK,
            tier=4,
            enchantment=0,
        )
        wood_cap_recipe = Recipe.objects.create(output=wood_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=wood_cap_recipe, object=ore, quantity=8)
        stone_cap_recipe = Recipe.objects.create(output=stone_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=stone_cap_recipe, object=ore, quantity=8)
        hide_cap_recipe = Recipe.objects.create(output=hide_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=hide_cap_recipe, object=ore, quantity=8)
        fish_cap_recipe = Recipe.objects.create(output=fish_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=fish_cap_recipe, object=leather, quantity=8)
        fish_garb_recipe = Recipe.objects.create(output=fish_garb, output_quantity=1)
        RecipeInput.objects.create(recipe=fish_garb_recipe, object=leather, quantity=8)
        fish_workboot_recipe = Recipe.objects.create(output=fish_workboot, output_quantity=1)
        RecipeInput.objects.create(recipe=fish_workboot_recipe, object=leather, quantity=8)
        fish_backpack_recipe = Recipe.objects.create(output=fish_backpack, output_quantity=1)
        RecipeInput.objects.create(recipe=fish_backpack_recipe, object=cloth, quantity=4)
        RecipeInput.objects.create(recipe=fish_backpack_recipe, object=leather, quantity=4)

        GatheringGearPriceRefreshService(fetcher=fetcher).refresh_prices(selected_resource_filter="ore")

        assert len(fetcher.requested_objects_batches) == 7
        flattened_requested_objects = {
            object_instance for batch in fetcher.requested_objects_batches for object_instance in batch
        }
        assert miner_cap in flattened_requested_objects
        assert miner_garb in flattened_requested_objects
        assert miner_workboot in flattened_requested_objects
        assert miner_backpack in flattened_requested_objects
        assert fiber_cap in flattened_requested_objects
        assert wood_cap in flattened_requested_objects
        assert stone_cap in flattened_requested_objects
        assert hide_cap in flattened_requested_objects
        assert fish_cap in flattened_requested_objects
        assert fish_garb in flattened_requested_objects
        assert fish_workboot in flattened_requested_objects
        assert fish_backpack in flattened_requested_objects
        assert metalbar in flattened_requested_objects
        assert cloth in flattened_requested_objects
        assert leather in flattened_requested_objects
        assert ore in flattened_requested_objects
