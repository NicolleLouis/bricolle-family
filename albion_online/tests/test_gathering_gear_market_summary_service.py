from datetime import timedelta

import pytest
from django.utils import timezone

from albion_online.constants.city import City
from albion_online.constants.object_type import ObjectType
from albion_online.models import Object, Price, Recipe, RecipeInput
from albion_online.services.gathering_gear_market_summary import GatheringGearMarketSummaryService


@pytest.mark.django_db
class TestGatheringGearMarketSummaryService:
    def test_build_rows_uses_buy_tax_and_sale_fees_in_detail_breakdown(self):
        now = timezone.now()
        miner_cap = Object.objects.create(
            aodp_id="TEST_T4_HEAD_GATHERER_ORE_SERVICE",
            name="Adept's Miner Cap",
            type_id=ObjectType.HEAD,
            tier=4,
            enchantment=2,
            crafting_tree="gatherer_ore_head",
        )
        metal_bar = Object.objects.create(
            aodp_id="TEST_T4_METALBAR_GATHERER_ORE_SERVICE@2",
            name="Adept's Metal Bar",
            type_id=ObjectType.METALBAR,
            tier=4,
            enchantment=2,
        )
        recipe = Recipe.objects.create(output=miner_cap, output_quantity=1)
        RecipeInput.objects.create(recipe=recipe, object=metal_bar, quantity=8)

        Price.objects.create(
            object=miner_cap,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=100,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=400,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=miner_cap,
            city=City.BRIDGEWATCH,
            quality=1,
            sell_price_min=200,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=500,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=miner_cap,
            city=City.BRIDGEWATCH,
            quality=2,
            sell_price_min=300,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=600,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=metal_bar,
            city=City.BRIDGEWATCH,
            quality=0,
            sell_price_min=4,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=8,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=metal_bar,
            city=City.BRIDGEWATCH,
            quality=1,
            sell_price_min=5,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=9,
            buy_price_max_date=now - timedelta(minutes=30),
        )
        Price.objects.create(
            object=metal_bar,
            city=City.BRIDGEWATCH,
            quality=2,
            sell_price_min=6,
            sell_price_min_date=now - timedelta(minutes=30),
            buy_price_max=10,
            buy_price_max_date=now - timedelta(minutes=30),
        )

        service = GatheringGearMarketSummaryService()
        rows = service.build_rows([miner_cap])
        detail_row = service.build_detail_row(miner_cap)

        bridgewatch_summary = next(summary for summary in rows[0]["city_summaries"] if summary.city == City.BRIDGEWATCH)
        bridgewatch_detail = next(detail for detail in detail_row["city_details"] if detail.city == City.BRIDGEWATCH)

        assert bridgewatch_summary.sell_price == 200
        assert bridgewatch_summary.craft_cost == 35
        assert bridgewatch_summary.craft_margin == 152
        assert bridgewatch_summary.craft_margin_class_name == "bg-success"
        assert bridgewatch_detail.raw_input_cost == 40
        assert bridgewatch_detail.input_cost_before_buy_tax == 34
        assert bridgewatch_detail.resource_return_amount == 6
        assert bridgewatch_detail.buy_tax_amount == 1
        assert bridgewatch_detail.sale_fee_amount == 13
        assert bridgewatch_detail.net_sell_price == 187
        assert bridgewatch_detail.input_details[0].raw_cost == 40
        assert bridgewatch_detail.input_details[0].resource_return_rate == pytest.approx(0.153)
        assert bridgewatch_detail.input_details[0].resource_return_amount == 6
        assert bridgewatch_detail.input_details[0].total_cost == 34
        assert [quality_detail.label for quality_detail in bridgewatch_detail.quality_details] == [
            "Normal",
            "Good",
            "Outstanding",
            "Excellent",
            "Masterpiece",
        ]
