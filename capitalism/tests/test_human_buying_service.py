import pytest

from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, Transaction
from capitalism.services.buying import HumanBuyingService


@pytest.mark.django_db
def test_buying_service_purchases_affordable_objects():
    initial_money = 30
    bread_1 = 1.5
    bread_2 = 1.0
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=initial_money)
    seller_one = Human.objects.create(money=0)
    seller_two = Human.objects.create(money=0)

    object_one = seller_one.owned_objects.create(
        type=ObjectType.BREAD,
        price=bread_1,
        in_sale=True,
    )
    object_two = seller_two.owned_objects.create(
        type=ObjectType.BREAD,
        price=bread_2,
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
    assert buyer.money == pytest.approx(initial_money-bread_2-bread_1)
    assert seller_one.money == pytest.approx(bread_1)
    assert seller_two.money == pytest.approx(bread_2)
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


@pytest.mark.django_db
def test_buying_service_recalculates_price_between_purchases():
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=20)
    cheap_seller = Human.objects.create(money=0)
    pricey_seller = Human.objects.create(money=0)

    cheap = cheap_seller.owned_objects.create(
        type=ObjectType.BREAD,
        price=4.0,
        in_sale=True,
    )
    pricey = pricey_seller.owned_objects.create(
        type=ObjectType.BREAD,
        price=8.0,
        in_sale=True,
    )

    HumanBuyingService(buyer).run()

    buyer.refresh_from_db()
    cheap_seller.refresh_from_db()
    pricey_seller.refresh_from_db()
    cheap.refresh_from_db()
    pricey.refresh_from_db()

    assert buyer.money == pytest.approx(16.0)
    assert cheap_seller.money == pytest.approx(4.0)
    assert pricey_seller.money == pytest.approx(0.0)
    assert cheap.owner == buyer
    assert pricey.owner == pricey_seller
    assert Transaction.objects.filter(object_type=ObjectType.BREAD).count() == 1


@pytest.mark.django_db
def test_total_money_preserved_across_transactions():
    buyers = [
        Human.objects.create(step=SimulationStep.BUYING, money=75 + idx * 5)
        for idx in range(4)
    ]
    sellers = [
        Human.objects.create(step=SimulationStep.SELLING, money=50)
        for _ in range(4)
    ]

    prices = [3.5, 5.25, 7.75, 6.0]
    for idx, seller in enumerate(sellers):
        for _ in range(2):
            seller.owned_objects.create(
                type=ObjectType.BREAD,
                price=prices[idx],
                in_sale=True,
            )

    initial_total = sum(Human.objects.values_list("money", flat=True))

    for buyer in buyers:
        HumanBuyingService(buyer).run()

    final_total = sum(Human.objects.values_list("money", flat=True))
    assert final_total == pytest.approx(initial_total, rel=1e-9)
