import pytest

from albion_online.constants.leather_jacket import LEATHER_JACKET_TYPES
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Recipe, RecipeInput
from albion_online.services.mercenary_jacket_price_refresh import (
    LeatherJacketPriceRefreshService,
)


class FakeFetcher:
    def __init__(self):
        self.requested_objects_batches = []
        self.request_log_sources = []

    def fetch_current_prices(self, objects, request_log_source="price_fetcher"):
        self.requested_objects_batches.append(list(objects))
        self.request_log_sources.append(request_log_source)
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
        stalker_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_MORGANA_REFRESH",
            name="Adept's Stalker Jacket",
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
        leather_folds = Object.objects.create(
            aodp_id="TEST_T4_ARTEFACT_ARMOR_LEATHER_MORGANA_REFRESH",
            name="Adept's Imbued Leather Folds",
            type_id=ObjectType.ARTEFACT,
            tier=4,
            enchantment=0,
        )
        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)
        stalker_recipe = Recipe.objects.create(output=stalker_jacket, output_quantity=1)
        RecipeInput.objects.create(recipe=stalker_recipe, object=leather, quantity=16)
        RecipeInput.objects.create(recipe=stalker_recipe, object=leather_folds, quantity=1)

        LeatherJacketPriceRefreshService(fetcher=fetcher).refresh_prices()

        assert len(fetcher.requested_objects_batches) == len(LEATHER_JACKET_TYPES) + 1
        assert set(fetcher.request_log_sources) == {"leather_jacket"}
        assert mercenary_jacket in fetcher.requested_objects_batches[0]
        assert hunter_jacket in fetcher.requested_objects_batches[1]
        assert assassin_jacket in fetcher.requested_objects_batches[2]
        assert stalker_jacket in fetcher.requested_objects_batches[3]
        assert leather in fetcher.requested_objects_batches[-1]
        assert leather_folds in fetcher.requested_objects_batches[-1]
