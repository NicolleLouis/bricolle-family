import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import PriceAnalytics


@pytest.mark.django_db
def test_price_analytics_creation():
    analytics = PriceAnalytics.objects.create(
        day_number=5,
        object_type=ObjectType.BREAD,
        lowest_price_displayed=1,
        max_price_displayed=5,
        average_price_displayed=3.2,
        lowest_price=1,
        max_price=4,
        average_price=2.5,
    )

    assert analytics.day_number == 5
    assert analytics.object_type == ObjectType.BREAD
    assert analytics.lowest_price_displayed == 1
    assert analytics.max_price_displayed == 5
    assert analytics.average_price_displayed == 3.2
    assert analytics.lowest_price == 1
    assert analytics.max_price == 4
    assert analytics.average_price == 2.5
