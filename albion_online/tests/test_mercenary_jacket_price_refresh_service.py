import pytest

from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Recipe, RecipeInput
from albion_online.services.mercenary_jacket_price_refresh import (
    LeatherJacketPriceRefreshService,
)


class FakeFetcher:
    def __init__(self):
        self.requested_objects_batches = []

    def fetch_current_prices(self, objects):
        self.requested_objects_batches.append(list(objects))
        return []


@pytest.mark.django_db
class TestLeatherJacketPriceRefreshService:
    def test_refresh_prices_fetches_all_leather_jackets_by_type(self):
        fetcher = FakeFetcher()
        mercenary_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1_REFRESH",
            name="Adept's Mercenary Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        hunter_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET2_REFRESH",
            name="Adept's Hunter Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        assassin_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET3_REFRESH",
            name="Adept's Assassin Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_LEVEL1_REFRESH@2",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=2,
            crafting_tree="leather_chest",
        )
        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)

        LeatherJacketPriceRefreshService(fetcher=fetcher).refresh_prices()

        assert len(fetcher.requested_objects_batches) == 4
        assert mercenary_jacket in fetcher.requested_objects_batches[0]
        assert hunter_jacket in fetcher.requested_objects_batches[1]
        assert assassin_jacket in fetcher.requested_objects_batches[2]
        assert leather in fetcher.requested_objects_batches[3]
