import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.services.pricing import GlobalPriceReferenceService


def test_reference_prices_known_objects():
    service = GlobalPriceReferenceService()
    assert service.get_reference_price(ObjectType.WHEAT) == 1.0
    assert service.get_reference_price(ObjectType.WOOD) == 2.0
    assert service.get_reference_price(ObjectType.BREAD) == 10.0
    assert service.get_reference_price(ObjectType.FLOUR) == 4.0
    assert service.get_reference_price(ObjectType.ORE) == 25.0
    assert service.get_reference_price(ObjectType.AXE) == 100.0


def test_reference_price_missing_raises():
    service = GlobalPriceReferenceService()
    with pytest.raises(GlobalPriceReferenceService.PriceNotFound):
        service.get_reference_price("unknown")
