import pytest

from capitalism.constants import ObjectType
from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human
from capitalism.services.pricing import HumanBuyingPriceValuationService


@pytest.fixture
def service():
    return HumanBuyingPriceValuationService()


@pytest.mark.django_db
def test_input_price_derived_from_expected_profit(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.FLOUR)

    assert pytest.approx(price, rel=1e-3) == 4.1


@pytest.mark.django_db
def test_consumption_need_decreases_with_stock(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)
    assert service.estimate_price(human, ObjectType.BREAD) == 7.0

    human.owned_objects.create(type=ObjectType.BREAD)

    assert pytest.approx(service.estimate_price(human, ObjectType.BREAD), rel=1e-3) == 3.5


@pytest.mark.django_db
def test_input_and_need_takes_highest_value(service):
    human = Human.objects.create(job=Job.TOOLMAKER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.WOOD)

    assert pytest.approx(price, rel=1e-3) == 381.0


@pytest.mark.django_db
def test_input_price_drops_but_consumption_value_remains(service):
    human = Human.objects.create(job=Job.TOOLMAKER, step=SimulationStep.PRODUCTION)
    for _ in range(5):
        human.owned_objects.create(type=ObjectType.WOOD)

    price = service.estimate_price(human, ObjectType.WOOD)

    assert pytest.approx(price, rel=1e-3) == 0.333


@pytest.mark.django_db
def test_object_without_need_or_input_has_zero_value(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)

    assert service.estimate_price(human, ObjectType.SCYTHE) == 0.0


@pytest.mark.django_db
def test_consumption_price_increases_with_unmet_needs(service):
    human = Human.objects.create(
        job=Job.MINER,
        step=SimulationStep.PRODUCTION,
        time_since_need_fulfilled=3,
    )

    price = service.estimate_price(human, ObjectType.BREAD)

    assert pytest.approx(price, rel=1e-3) == 11.2
