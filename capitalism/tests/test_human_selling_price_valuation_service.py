import pytest

from capitalism.constants import ObjectType
from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human
from capitalism.services.pricing import HumanSellingPriceValuationService


@pytest.fixture
def service():
    return HumanSellingPriceValuationService()


@pytest.mark.django_db
def test_valuation_for_miner_with_tool(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.PICKAXE)

    price = service.estimate_price(human, ObjectType.ORE)

    assert pytest.approx(price, rel=1e-3) == 1.44


@pytest.mark.django_db
def test_valuation_for_miner_without_tool_is_higher(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.ORE)

    assert pytest.approx(price, rel=1e-3) == 14.4


@pytest.mark.django_db
def test_stock_adjustment_decreases_price_when_surplus(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.SPATULA)
    for _ in range(50):
        human.owned_objects.create(type=ObjectType.BREAD)

    price = service.estimate_price(human, ObjectType.BREAD)

    assert price < 6


def test_unknown_object_type_returns_none(service):
    price = service.estimate_price(None, "unknown")

    assert price is None


@pytest.mark.django_db
def test_object_not_produced_by_human_returns_none(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.BREAD)

    assert price is None
