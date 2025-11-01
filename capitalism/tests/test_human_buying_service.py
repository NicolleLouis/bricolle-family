import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, Transaction
from capitalism.services.buying import HumanBuyingService


@pytest.mark.django_db
def test_buying_service_purchases_affordable_objects():
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=30)
    seller_one = Human.objects.create(money=0)
    seller_two = Human.objects.create(money=0)

    object_one = seller_one.owned_objects.create(
        type=ObjectType.BREAD,
        price=8.75,
        in_sale=True,
    )
    object_two = seller_two.owned_objects.create(
        type=ObjectType.BREAD,
        price=7.5,
        in_sale=True,
    )

    next_step = HumanBuyingService(buyer).run()

    buyer.refresh_from_db()
    seller_one.refresh_from_db()
    seller_two.refresh_from_db()
    object_one.refresh_from_db()
    object_two.refresh_from_db()

    assert next_step == SimulationStep.CONSUMPTION
    assert buyer.step == SimulationStep.CONSUMPTION
    assert buyer.money == pytest.approx(13.75)
    assert seller_one.money == pytest.approx(8.75)
    assert seller_two.money == pytest.approx(7.5)
    assert object_one.owner == buyer
    assert object_two.owner == buyer
    assert object_one.in_sale is False
    assert object_two.in_sale is False
    assert object_one.price is None
    assert object_two.price is None
    assert Transaction.objects.count() == 2


@pytest.mark.django_db
def test_buying_service_skips_unaffordable_or_overpriced_objects():
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=5)
    seller = Human.objects.create(money=0)

    expensive = seller.owned_objects.create(
        type=ObjectType.BREAD,
        price=8,
        in_sale=True,
    )
    overpriced = seller.owned_objects.create(
        type=ObjectType.WOOD,
        price=3,
        in_sale=True,
    )

    HumanBuyingService(buyer).run()

    buyer.refresh_from_db()
    seller.refresh_from_db()
    expensive.refresh_from_db()
    overpriced.refresh_from_db()

    assert buyer.step == SimulationStep.CONSUMPTION
    assert buyer.money == 5
    assert seller.money == 0
    assert expensive.owner == seller
    assert overpriced.owner == seller
    assert expensive.in_sale is True
    assert overpriced.in_sale is True
    assert expensive.price == 8
    assert overpriced.price == 3
    assert Transaction.objects.count() == 0


class _FixedPriceValuation:
    def __init__(self, price_map: dict[str, float]):
        self.price_map = price_map

    def estimate_price(self, _human, object_type: str) -> float:
        return self.price_map.get(object_type, 0.0)


@pytest.mark.django_db
def test_seller_receives_payment_for_every_transaction():
    seller = Human.objects.create(money=150)
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=150)

    for _ in range(10):
        seller.owned_objects.create(
            type=ObjectType.WHEAT,
            price=0.84,
            in_sale=True,
        )

    valuation = _FixedPriceValuation({ObjectType.WHEAT: 1.0})

    HumanBuyingService(buyer, valuation_service=valuation).run()

    seller.refresh_from_db()
    buyer.refresh_from_db()

    assert buyer.money == pytest.approx(150 - 0.84 * 10, rel=1e-6)
    assert seller.money == pytest.approx(150 + 0.84 * 10, rel=1e-6)
    assert Transaction.objects.filter(object_type=ObjectType.WHEAT).count() == 10
