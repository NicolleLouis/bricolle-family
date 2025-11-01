import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, PriceAnalytics
from capitalism.services.pricing import PriceAnalyticsRecorderService


@pytest.mark.django_db
def test_price_analytics_recorder_populates_all_object_types():
    human = Human.objects.create(step=SimulationStep.PRICE_STATS)
    human.owned_objects.create(type=ObjectType.WOOD, in_sale=True, price=5.0)
    human.owned_objects.create(type=ObjectType.WOOD, in_sale=True, price=15.0)
    human.owned_objects.create(type=ObjectType.BREAD, in_sale=False, price=100.0)

    PriceAnalyticsRecorderService(day_number=7).run()

    analytics = PriceAnalytics.objects.filter(day_number=7)
    assert analytics.count() == len(ObjectType.choices)

    wood_stats = analytics.get(object_type=ObjectType.WOOD)
    assert wood_stats.lowest_price_displayed == pytest.approx(5.0)
    assert wood_stats.max_price_displayed == pytest.approx(15.0)
    assert wood_stats.average_price_displayed == pytest.approx(10.0)
    assert wood_stats.lowest_price == pytest.approx(0.0)
    assert wood_stats.max_price == pytest.approx(0.0)
    assert wood_stats.average_price == pytest.approx(0.0)
    assert wood_stats.transaction_number == 0

    bread_stats = analytics.get(object_type=ObjectType.BREAD)
    assert bread_stats.lowest_price_displayed == pytest.approx(0.0)
    assert bread_stats.max_price_displayed == pytest.approx(0.0)
    assert bread_stats.average_price_displayed == pytest.approx(0.0)
    assert bread_stats.lowest_price == pytest.approx(0.0)
    assert bread_stats.max_price == pytest.approx(0.0)
    assert bread_stats.average_price == pytest.approx(0.0)
    assert bread_stats.transaction_number == 0


@pytest.mark.django_db
def test_price_analytics_recorder_ignores_unsuitable_objects():
    seller = Human.objects.create(step=SimulationStep.PRICE_STATS)
    seller.owned_objects.create(type=ObjectType.ORE, in_sale=False, price=12.0)
    seller.owned_objects.create(type=ObjectType.ORE, in_sale=True, price=None)
    seller.owned_objects.create(type=ObjectType.ORE, in_sale=True, price=8.0)

    PriceAnalyticsRecorderService(day_number=3).run()

    ore_stats = PriceAnalytics.objects.get(day_number=3, object_type=ObjectType.ORE)
    assert ore_stats.lowest_price_displayed == pytest.approx(8.0)
    assert ore_stats.max_price_displayed == pytest.approx(8.0)
    assert ore_stats.average_price_displayed == pytest.approx(8.0)
    assert ore_stats.lowest_price == pytest.approx(0.0)
    assert ore_stats.max_price == pytest.approx(0.0)
    assert ore_stats.average_price == pytest.approx(0.0)
    assert ore_stats.transaction_number == 0
