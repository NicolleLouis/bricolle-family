import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import Human
from capitalism.services.object_statistics import ObjectInventoryStatisticsService


@pytest.mark.django_db
def test_object_inventory_statistics_computes_counts_and_prices():
    human = Human.objects.create(name="Stats Owner")
    human.owned_objects.create(type=ObjectType.WHEAT, price=2.0, in_sale=True)
    human.owned_objects.create(type=ObjectType.WHEAT, price=4.0, in_sale=False)
    human.owned_objects.create(type=ObjectType.BREAD, price=None, in_sale=False)

    stats = ObjectInventoryStatisticsService().run()
    stats_map = {entry["type"]: entry for entry in stats}

    wheat_stats = stats_map[ObjectType.WHEAT]
    assert wheat_stats["quantity"] == 2
    assert wheat_stats["min_price"] == pytest.approx(2.0)
    assert wheat_stats["avg_price"] == pytest.approx(3.0)
    assert wheat_stats["max_price"] == pytest.approx(4.0)

    bread_stats = stats_map[ObjectType.BREAD]
    assert bread_stats["quantity"] == 1
    assert bread_stats["min_price"] is None
    assert bread_stats["avg_price"] is None
    assert bread_stats["max_price"] is None

    # Ensure types without objects report zero
    axe_stats = stats_map[ObjectType.AXE]
    assert axe_stats["quantity"] == 0
    assert axe_stats["min_price"] is None
