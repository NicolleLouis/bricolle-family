import pytest

from capitalism.constants import ObjectType
from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human
from capitalism.services.pricing import HumanSellingPriceValuationService
from capitalism.services.pricing.production_time_cost import time_cost_per_unit
from capitalism.services.jobs import Miner, Baker


@pytest.fixture
def service():
    return HumanSellingPriceValuationService()


@pytest.mark.django_db
def test_valuation_for_miner_with_tool(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.PICKAXE)

    price = service.estimate_price(human, ObjectType.ORE)

    expected_unit_cost = time_cost_per_unit(human, Miner) + service._input_cost_per_unit(Miner)
    assert pytest.approx(price, rel=1e-3) == expected_unit_cost * (1 + service.MARKUP_BASE)


@pytest.mark.django_db
def test_valuation_for_miner_without_tool_is_higher(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.ORE)

    expected_unit_cost = time_cost_per_unit(human, Miner) + service._input_cost_per_unit(Miner)
    assert pytest.approx(price, rel=1e-3) == expected_unit_cost * (1 + service.MARKUP_BASE)


@pytest.mark.django_db
def test_stock_adjustment_decreases_price_when_surplus(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.SPATULA)
    for _ in range(50):
        human.owned_objects.create(type=ObjectType.BREAD)

    price = service.estimate_price(human, ObjectType.BREAD)

    expected_unit_cost = time_cost_per_unit(human, Baker) + service._input_cost_per_unit(Baker)
    stock_effect = service._stock_effect(human, Baker, ObjectType.BREAD)
    expected_price = expected_unit_cost * (1 + service.MARKUP_BASE - stock_effect)
    assert pytest.approx(price, rel=1e-3) == expected_price
    assert price < expected_unit_cost * (1 + service.MARKUP_BASE)


@pytest.mark.django_db
def test_unknown_object_type_returns_none(service):
    price = service.estimate_price(None, "unknown")

    assert price is None


@pytest.mark.django_db
def test_object_not_produced_by_human_returns_none(service):
    human = Human.objects.create(job=Job.MINER, step=SimulationStep.PRODUCTION)

    price = service.estimate_price(human, ObjectType.BREAD)

    assert price is None


@pytest.mark.django_db
def test_equivalent_stock_days_accounts_for_tool(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.SPATULA)
    for _ in range(40):
        human.owned_objects.create(type=ObjectType.BREAD)

    n_days = service._equivalent_stock_days(human, Baker, ObjectType.BREAD)

    assert pytest.approx(n_days, rel=1e-3) == 2.0


@pytest.mark.django_db
def test_stock_effect_capped_at_one(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.SPATULA)
    for _ in range(200):
        human.owned_objects.create(type=ObjectType.BREAD)

    stock_effect = service._stock_effect(human, Baker, ObjectType.BREAD)

    assert pytest.approx(stock_effect, rel=1e-3) == 1.0


@pytest.mark.django_db
def test_stock_effect_reduces_final_price(service):
    human = Human.objects.create(job=Job.BAKER, step=SimulationStep.PRODUCTION)
    human.owned_objects.create(type=ObjectType.SPATULA)
    for _ in range(100):
        human.owned_objects.create(type=ObjectType.BREAD)

    price = service.estimate_price(human, ObjectType.BREAD)

    unit_cost = time_cost_per_unit(human, Baker) + service._input_cost_per_unit(Baker)
    stock_effect = service._stock_effect(human, Baker, ObjectType.BREAD)
    expected_price = unit_cost * (1 + service.MARKUP_BASE - stock_effect)

    assert pytest.approx(price, rel=1e-3) == expected_price
