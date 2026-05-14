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
    def test_refresh_prices_fetches_selected_resource_group_and_recipe_inputs(self):
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

        GatheringGearPriceRefreshService(fetcher=fetcher).refresh_prices(selected_resource_filter="ore")

        assert len(fetcher.requested_objects_batches) == 2
        assert miner_cap in fetcher.requested_objects_batches[0]
        assert miner_garb in fetcher.requested_objects_batches[0]
        assert miner_workboot in fetcher.requested_objects_batches[0]
        assert miner_backpack in fetcher.requested_objects_batches[0]
        assert fiber_cap not in fetcher.requested_objects_batches[0]
        assert metalbar in fetcher.requested_objects_batches[-1]
        assert cloth in fetcher.requested_objects_batches[-1]
        assert leather in fetcher.requested_objects_batches[-1]
