import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.models import MarketPerceivedPrice
from capitalism.services.pricing import (
    GlobalPriceReferenceService,
    MarketPerceivedPriceResetService,
)


@pytest.mark.django_db
def test_reference_prices_known_objects():
    MarketPerceivedPriceResetService(day_number=0).reset()
    service = GlobalPriceReferenceService()

    assert service.get_reference_price(ObjectType.WHEAT) == 1.0
    assert service.get_reference_price(ObjectType.WOOD) == 2.0
    assert service.get_reference_price(ObjectType.BREAD) == 7.0
    assert service.get_reference_price(ObjectType.FLOUR) == 4.0
    assert service.get_reference_price(ObjectType.ORE) == 10.0
    assert service.get_reference_price(ObjectType.AXE) == 100.0


@pytest.mark.django_db
def test_reference_price_uses_database_values():
    MarketPerceivedPriceResetService(day_number=0).reset()
    MarketPerceivedPrice.objects.filter(object=ObjectType.BREAD).update(perceived_price=12.5)

    service = GlobalPriceReferenceService()
    assert service.get_reference_price(ObjectType.BREAD) == pytest.approx(12.5)


@pytest.mark.django_db
def test_reference_price_missing_raises():
    service = GlobalPriceReferenceService()
    with pytest.raises(GlobalPriceReferenceService.PriceNotFound):
        service.get_reference_price("unknown")
