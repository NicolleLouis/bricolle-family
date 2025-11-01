import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, MarketPerceivedPrice
from capitalism.services.object_statistics import ObjectInventoryStatisticsService
from capitalism.services.pricing import MarketPerceivedPriceResetService


@pytest.mark.django_db
def test_object_inventory_statistics_reports_quantity_and_perceived_price():
    MarketPerceivedPriceResetService(day_number=0).reset()
    MarketPerceivedPrice.objects.filter(object=ObjectType.WHEAT).update(perceived_price=3.5)

    human = Human.objects.create(name="Stats Owner")
    human.owned_objects.create(type=ObjectType.WHEAT, price=2.0, in_sale=True)
    human.owned_objects.create(type=ObjectType.WHEAT, price=4.0, in_sale=False)
    human.owned_objects.create(type=ObjectType.BREAD, price=None, in_sale=False)

    stats = ObjectInventoryStatisticsService().run()
    stats_map = {entry["type"]: entry for entry in stats}

    wheat_stats = stats_map[ObjectType.WHEAT]
    assert wheat_stats["quantity"] == 2
    assert wheat_stats["perceived_price"] == pytest.approx(3.5)

    bread_stats = stats_map[ObjectType.BREAD]
    assert bread_stats["quantity"] == 1
    assert bread_stats["perceived_price"] == pytest.approx(7.0)

    axe_stats = stats_map[ObjectType.AXE]
    assert axe_stats["quantity"] == 0
    assert axe_stats["perceived_price"] == pytest.approx(100.0)
