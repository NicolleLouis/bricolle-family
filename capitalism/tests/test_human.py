import pytest

from capitalism.constants.jobs import Job
from capitalism.constants.object_type import ObjectType
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, ObjectStack
from capitalism.services.production.service import ProductionService
from capitalism.services.pricing import HumanSellingPriceValuationService
from capitalism.services.selling import HumanSellingService


class _FixedRandom:
    def __init__(self, value):
        self.value = value

    def random(self):
        return self.value


@pytest.mark.django_db
def test_human_defaults():
    human = Human.objects.create()

    assert human.age == 0
    assert human.job == Job.MINER
    assert human.money == 150
    assert human.time_since_need_fulfilled == 0
    assert human.time_without_full_needs == 0
    assert human.step == SimulationStep.START_OF_DAY
    assert human.dead is False


@pytest.mark.django_db
def test_human_next_step_progression():
    human = Human.objects.create(step=SimulationStep.PRODUCTION)

    assert human.next_step() == SimulationStep.SELLING
    human.refresh_from_db()
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_human_next_step_wraps_to_start():
    human = Human.objects.create(step=SimulationStep.END_OF_DAY)

    assert human.next_step() == SimulationStep.START_OF_DAY
    human.refresh_from_db()
    assert human.step == SimulationStep.START_OF_DAY


@pytest.mark.django_db
def test_production_without_tool_uses_base_capacity():
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.MINER)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.get_object_quantity(ObjectType.ORE) == 1
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_production_with_tool_creates_outputs(monkeypatch):
    monkeypatch.setattr(ProductionService, "random_generator", _FixedRandom(0.9))
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.MINER)
    human.add_objects(ObjectType.PICKAXE, 1)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.get_object_quantity(ObjectType.ORE) == 10
    assert human.get_object_quantity(ObjectType.PICKAXE) == 1
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_farmer_production_generates_wood_and_advances_step():
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.FARMER)

    human.perform_production()
    human.refresh_from_db()

    assert human.step == SimulationStep.SELLING
    assert human.get_object_quantity(ObjectType.WHEAT) == 10


@pytest.mark.django_db
def test_production_tool_breaks_when_probability_hits(monkeypatch):
    monkeypatch.setattr(ProductionService, "random_generator", _FixedRandom(0.001))
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.MINER)
    human.add_objects(ObjectType.PICKAXE, 1)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.get_object_quantity(ObjectType.ORE) == 10
    assert human.get_object_quantity(ObjectType.PICKAXE) == 0
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_production_tool_survives_when_probability_misses(monkeypatch):
    monkeypatch.setattr(ProductionService, "random_generator", _FixedRandom(0.5))
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.MINER)
    human.add_objects(ObjectType.PICKAXE, 1)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.get_object_quantity(ObjectType.PICKAXE) == 1
    assert human.get_object_quantity(ObjectType.ORE) == 10
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_production_limited_by_inputs(monkeypatch):
    monkeypatch.setattr(ProductionService, "random_generator", _FixedRandom(0.9))
    human = Human.objects.create(step=SimulationStep.PRODUCTION, job=Job.BAKER)
    human.add_objects(ObjectType.SPATULA, 1)

    for _ in range(3):
        human.add_objects(ObjectType.FLOUR, 1)
        human.add_objects(ObjectType.WOOD, 1)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.get_object_quantity(ObjectType.FLOUR) == 0
    assert human.get_object_quantity(ObjectType.WOOD) == 0
    assert human.get_object_quantity(ObjectType.BREAD) == 3
    assert human.step == SimulationStep.SELLING


@pytest.mark.django_db
def test_perform_selling_resets_inventory_and_lists_sellable_objects():
    human = Human.objects.create(step=SimulationStep.SELLING, job=Job.MINER)
    human.owned_objects.create(type=ObjectType.ORE, price=5, in_sale=True, quantity=2)
    human.owned_objects.create(type=ObjectType.BREAD, price=12, in_sale=True, quantity=2)

    expected_price = HumanSellingPriceValuationService().estimate_price(human, ObjectType.ORE)
    assert expected_price is not None
    expected_price = HumanSellingService._format_price(expected_price)

    next_step = human.perform_selling()
    human.refresh_from_db()

    assert next_step == SimulationStep.PRICE_STATS
    assert human.step == SimulationStep.PRICE_STATS
    assert human.owned_objects.filter(type=ObjectType.ORE, in_sale=True).total_quantity() == 1
    assert human.owned_objects.filter(type=ObjectType.ORE, in_sale=False).total_quantity() == 1
    assert (
        human.owned_objects.filter(type=ObjectType.ORE, in_sale=True)
        .values_list("price", flat=True)
        .distinct()
        .get()
        == pytest.approx(expected_price, rel=1e-6)
    )
    assert human.owned_objects.filter(type=ObjectType.BREAD, in_sale=True).exists() is False
    assert human.owned_objects.filter(type=ObjectType.BREAD, price__isnull=False).exists() is False


@pytest.mark.django_db
def test_perform_selling_rounds_price_to_two_decimals(monkeypatch):
    human = Human.objects.create(step=SimulationStep.SELLING, job=Job.MINER)
    human.owned_objects.create(type=ObjectType.ORE, price=0, in_sale=False, quantity=2)

    def fake_estimate_price(self, _human, _type):
        return 5.6789

    monkeypatch.setattr(
        HumanSellingPriceValuationService,
        "estimate_price",
        fake_estimate_price,
    )

    human.perform_current_step()
    human.refresh_from_db()

    sale_stack = human.owned_objects.filter(type=ObjectType.ORE, in_sale=True).first()
    assert sale_stack is not None
    assert sale_stack.price == pytest.approx(5.68)


@pytest.mark.django_db
def test_perform_selling_keeps_basic_needs_out_of_sale():
    human = Human.objects.create(step=SimulationStep.SELLING, job=Job.BAKER)
    human.owned_objects.create(type=ObjectType.BREAD, price=3.0, in_sale=True, quantity=3)

    human.perform_selling()
    human.refresh_from_db()

    assert human.owned_objects.filter(type=ObjectType.BREAD, in_sale=True).total_quantity() == 1
    assert human.owned_objects.filter(type=ObjectType.BREAD, in_sale=False).total_quantity() == 2
    assert human.owned_objects.filter(type=ObjectType.BREAD, in_sale=False, price__isnull=False).exists() is False


@pytest.mark.django_db
def test_use_basic_need_consumes_items_and_resets_counter():
    human = Human.objects.create(time_since_need_fulfilled=3, time_without_full_needs=5)
    ObjectStack.objects.create(owner=human, type=ObjectType.WOOD)
    ObjectStack.objects.create(owner=human, type=ObjectType.BREAD)

    human.use_basic_need()
    human.refresh_from_db()

    assert human.owned_objects.total_quantity() == 0
    assert human.time_since_need_fulfilled == 0
    assert human.time_without_full_needs == 5
    assert human.step == SimulationStep.START_OF_DAY


@pytest.mark.django_db
def test_use_basic_need_missing_item_increments_counters():
    human = Human.objects.create(time_since_need_fulfilled=0, time_without_full_needs=2)
    ObjectStack.objects.create(owner=human, type=ObjectType.WOOD)

    human.use_basic_need()
    human.refresh_from_db()

    assert human.time_since_need_fulfilled == 1
    assert human.time_without_full_needs == 3
    assert human.step == SimulationStep.START_OF_DAY


@pytest.mark.django_db
def test_perform_consumption_advances_step():
    human = Human.objects.create(step=SimulationStep.CONSUMPTION, time_since_need_fulfilled=2)
    ObjectStack.objects.create(owner=human, type=ObjectType.WOOD)
    ObjectStack.objects.create(owner=human, type=ObjectType.BREAD)

    human.perform_current_step()
    human.refresh_from_db()

    assert human.step == SimulationStep.DEATH
    assert human.time_since_need_fulfilled == 0


@pytest.mark.django_db
def test_perform_buying_advances_step_and_transfers_objects():
    bread_price = 1
    initial_money = 30
    buyer = Human.objects.create(step=SimulationStep.BUYING, money=initial_money)
    seller = Human.objects.create(money=0)
    offer = seller.owned_objects.create(type=ObjectType.BREAD, price=bread_price, in_sale=True)

    buyer.perform_current_step()

    buyer.refresh_from_db()
    seller.refresh_from_db()
    assert buyer.step == SimulationStep.CONSUMPTION
    assert buyer.money == initial_money - bread_price
    assert seller.money == bread_price
    assert buyer.get_object_quantity(ObjectType.BREAD) == 1
    assert seller.get_object_quantity(ObjectType.BREAD) == 0
    assert buyer.owned_objects.filter(id=offer.id).exists() is False


@pytest.mark.django_db
def test_perform_death_moves_to_analytics_when_threshold_exceeded():
    human = Human.objects.create(
        step=SimulationStep.DEATH,
        time_since_need_fulfilled=Human.DAY_STREAK_WITHOUT_NEED_LIMIT + 1,
    )

    human.perform_current_step()
    human.refresh_from_db()

    assert human.step == SimulationStep.ANALYTICS
    assert human.dead is True


@pytest.mark.django_db
def test_has_recently_fulfilled_basic_needs_property():
    newborn = Human.objects.create(age=0, time_since_need_fulfilled=0)
    assert newborn.has_recently_fulfilled_basic_needs is None

    satisfied = Human.objects.create(age=2, time_since_need_fulfilled=0)
    assert satisfied.has_recently_fulfilled_basic_needs is True

    deprived = Human.objects.create(age=3, time_since_need_fulfilled=4)
    assert deprived.has_recently_fulfilled_basic_needs is False
