from datetime import timedelta

import pytest
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, ObjectTypeGroup, Price, Recipe, RecipeInput
from albion_online.services.mercenary_jacket_market_summary import (
    MercenaryJacketMarketSummaryService,
)


@pytest.mark.django_db
class TestMercenaryJacketMarketSummaryService:
    def test_build_rows_averages_only_qualities_zero_to_two_per_city(self):
        now = timezone.now()
        mercenary_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1_SERVICE",
            name="Adept's Mercenary Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=2,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_LEVEL1_SERVICE@2",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=2,
            crafting_tree="leather_chest",
        )
        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)

        Price.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=100,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=400,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            quality=1,
            sell_price_min=200,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=500,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            quality=2,
            sell_price_min=300,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=600,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            quality=3,
            sell_price_min=900,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=900,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=leather,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=4,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=8,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=leather,
            city=City.BRIDGEWATCH,
            quality=1,
            sell_price_min=5,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=9,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=leather,
            city=City.BRIDGEWATCH,
            quality=2,
            sell_price_min=6,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=10,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.CAERLEON,
            quality=0,
            sell_price_min=1000,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=1300,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.CAERLEON,
            quality=1,
            sell_price_min=1100,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=1400,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.CAERLEON,
            quality=2,
            sell_price_min=1200,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=1500,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=leather,
            city=City.CAERLEON,
            quality=0,
            sell_price_min=100,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=130,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=leather,
            city=City.CAERLEON,
            quality=1,
            sell_price_min=100,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=140,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=leather,
            city=City.CAERLEON,
            quality=2,
            sell_price_min=100,
            sell_price_min_date=now - timedelta(hours=2),
            buy_price_max=150,
            buy_price_max_date=now - timedelta(hours=2),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.MARTLOCK,
            quality=0,
            sell_price_min=2000,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=2300,
            buy_price_max_date=now - timedelta(days=2),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.MARTLOCK,
            quality=1,
            sell_price_min=2100,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=2400,
            buy_price_max_date=now - timedelta(days=2),
        )
        Price.objects.create(
            object=mercenary_jacket,
            city=City.MARTLOCK,
            quality=2,
            sell_price_min=2200,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=2500,
            buy_price_max_date=now - timedelta(days=2),
        )
        Price.objects.create(
            object=leather,
            city=City.MARTLOCK,
            quality=0,
            sell_price_min=50,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=80,
            buy_price_max_date=now - timedelta(days=2),
        )
        Price.objects.create(
            object=leather,
            city=City.MARTLOCK,
            quality=1,
            sell_price_min=50,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=90,
            buy_price_max_date=now - timedelta(days=2),
        )
        Price.objects.create(
            object=leather,
            city=City.MARTLOCK,
            quality=2,
            sell_price_min=50,
            sell_price_min_date=now - timedelta(days=2),
            buy_price_max=100,
            buy_price_max_date=now - timedelta(days=2),
        )

        rows = MercenaryJacketMarketSummaryService().build_rows([mercenary_jacket])

        assert len(rows) == 1
        city_summaries = rows[0]["city_summaries"]

        bridgewatch_summary = next(summary for summary in city_summaries if summary.city == City.BRIDGEWATCH)
        caerleon_summary = next(summary for summary in city_summaries if summary.city == City.CAERLEON)
        martlock_summary = next(summary for summary in city_summaries if summary.city == City.MARTLOCK)
        bridgewatch_detail = next(detail for detail in rows[0]["city_details"] if detail.city == City.BRIDGEWATCH)

        assert bridgewatch_summary.sell_price == 200
        assert bridgewatch_summary.craft_cost == 69
        assert bridgewatch_summary.craft_margin == 127
        assert bridgewatch_summary.craft_margin_percent == 184.05797101449275
        assert bridgewatch_summary.craft_margin_class_name == "bg-success"
        assert bridgewatch_summary.sell_price_freshness["label"] == "Info fiable"
        assert bridgewatch_detail.input_details[0].label == "Leather 4.2"
        assert bridgewatch_detail.input_details[0].quantity == 16
        assert bridgewatch_detail.input_details[0].sell_price == 5
        assert bridgewatch_detail.input_details[0].total_cost == 68
        assert [quality_detail.label for quality_detail in bridgewatch_detail.quality_details] == [
            "Normal",
            "Good",
            "Outstanding",
            "Excellent",
            "Masterpiece",
        ]
        assert caerleon_summary.sell_price == 1100
        assert caerleon_summary.craft_cost == 1382
        assert caerleon_summary.craft_margin == -304
        assert caerleon_summary.craft_margin_percent == -21.99710564399421
        assert caerleon_summary.craft_margin_class_name == "bg-danger"
        assert caerleon_summary.sell_price_freshness["label"] == "Info > 1 heure"
        assert martlock_summary.is_hidden is True
        assert martlock_summary.sell_price == 2100
        assert martlock_summary.craft_cost is None
        assert martlock_summary.craft_margin is None
        assert martlock_summary.craft_margin_class_name is None
        assert martlock_summary.sell_price_freshness["label"] == "Info > 1 jour"
        martlock_detail = next(detail for detail in rows[0]["city_details"] if detail.city == City.MARTLOCK)
        assert martlock_detail.is_hidden is True
        assert martlock_detail.craft_cost == 692
        assert martlock_detail.craft_margin == 1366

    def test_build_rows_applies_city_specific_resource_return_rate_from_object_type_group(self):
        now = timezone.now()
        mercenary_jacket = Object.objects.create(
            aodp_id="TEST_T4_ARMOR_LEATHER_SET1_RRR",
            name="Adept's Mercenary Jacket",
            type_id=ObjectType.ARMOR,
            tier=4,
            enchantment=0,
            equipment_category="CHEST",
            crafting_tree="leather_chest",
        )
        mercenary_type = ObjectTypeGroup.objects.get(code=ObjectType.ARMOR)
        mercenary_type.resource_return_rate_city = City.BRIDGEWATCH
        mercenary_type.save(update_fields=["resource_return_rate_city"])
        leather = Object.objects.create(
            aodp_id="TEST_T4_LEATHER_LEVEL1_RRR",
            name="Adept's Leather",
            type_id=ObjectType.LEATHER,
            tier=4,
            enchantment=0,
            crafting_tree="leather_chest",
        )
        recipe = Recipe.objects.create(output=mercenary_jacket, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=leather, quantity=16)

        Price.objects.create(
            object=mercenary_jacket,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=300,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=400,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=leather,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=10,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=20,
            buy_price_max_date=now - timedelta(minutes=30),
        )

        rows = MercenaryJacketMarketSummaryService().build_rows([mercenary_jacket])

        bridgewatch_summary = next(summary for summary in rows[0]["city_summaries"] if summary.city == City.BRIDGEWATCH)
        bridgewatch_detail = next(detail for detail in rows[0]["city_details"] if detail.city == City.BRIDGEWATCH)

        assert bridgewatch_detail.input_details[0].total_cost == 101
        assert bridgewatch_summary.craft_cost == 103
