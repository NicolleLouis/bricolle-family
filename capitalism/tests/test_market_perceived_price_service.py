import pytest
from django.db import IntegrityError

from capitalism.constants.object_type import ObjectType
from capitalism.models import MarketPerceivedPrice, PriceAnalytics
from capitalism.services.pricing import (
    GlobalPriceReferenceService,
    MarketPerceivedPriceResetService,
    MarketPerceivedPriceUpdateService,
)


@pytest.mark.django_db
def test_reset_service_reinitializes_reference_prices():
    MarketPerceivedPrice.objects.create(
        updated_at=5,
        object=ObjectType.BREAD,
        perceived_price=999.0,
    )

    MarketPerceivedPriceResetService(day_number=3).reset()

    assert MarketPerceivedPrice.objects.count() == len(ObjectType.choices)

    reference = GlobalPriceReferenceService()
    for object_type, _label in ObjectType.choices:
        price = MarketPerceivedPrice.objects.get(object=object_type)
        assert price.updated_at == 3
        assert price.perceived_price == pytest.approx(
            reference.get_reference_price(object_type)
        )


@pytest.mark.django_db
def test_unique_constraint_enforced():
    MarketPerceivedPrice.objects.create(
        updated_at=1,
        object=ObjectType.WOOD,
        perceived_price=12.0,
    )

    with pytest.raises(IntegrityError):
        MarketPerceivedPrice.objects.create(
            updated_at=2,
            object=ObjectType.WOOD,
            perceived_price=15.0,
        )


@pytest.mark.django_db
def test_update_service_updates_day_and_preserves_price_without_analytics():
    MarketPerceivedPriceResetService(day_number=5).reset()
    MarketPerceivedPrice.objects.filter(object=ObjectType.AXE).update(
        perceived_price=120.0,
        updated_at=42,
    )

    MarketPerceivedPriceUpdateService(day_number=7).update()

    axe = MarketPerceivedPrice.objects.get(object=ObjectType.AXE)
    assert axe.updated_at == 7
    assert axe.perceived_price == pytest.approx(120.0)


@pytest.mark.django_db
def test_update_service_averages_with_price_analytics():
    day_number = 6
    MarketPerceivedPriceResetService(day_number=day_number).reset()
    MarketPerceivedPrice.objects.filter(object=ObjectType.BREAD).update(perceived_price=9.0)

    PriceAnalytics.objects.create(
        day_number=day_number,
        object_type=ObjectType.BREAD,
        lowest_price_displayed=0.0,
        max_price_displayed=0.0,
        average_price_displayed=6.0,
        lowest_price=0.0,
        max_price=0.0,
        average_price=12.0,
        transaction_number=4,
    )

    service = MarketPerceivedPriceUpdateService(day_number=day_number)
    service.update()

    bread = MarketPerceivedPrice.objects.get(object=ObjectType.BREAD)
    total_weight = (
        service.WEIGHT_CURRENT
        + service.WEIGHT_AVERAGE_PRICE
        + service.WEIGHT_DISPLAYED_AVERAGE
    )
    expected = (
        9.0 * service.WEIGHT_CURRENT
        + 12.0 * service.WEIGHT_AVERAGE_PRICE
        + 6.0 * service.WEIGHT_DISPLAYED_AVERAGE
    ) / total_weight
    assert bread.perceived_price == pytest.approx(expected)
    assert bread.updated_at == day_number
