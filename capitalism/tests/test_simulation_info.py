import pytest

from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Simulation, Human


@pytest.mark.django_db
def test_simulation_defaults():
    simulation = Simulation.objects.create()

    assert simulation.day_number == 0
    assert simulation.step == SimulationStep.START_OF_DAY
    assert simulation.can_change_step() is True


@pytest.mark.django_db
def test_simulation_next_step_cycles_through_sequence():
    simulation = Simulation.objects.create(step=SimulationStep.PRICE_STATS)

    Human.objects.create(step=SimulationStep.BUYING)
    next_step = simulation.next_step()
    assert next_step == SimulationStep.BUYING
    simulation.refresh_from_db()
    assert simulation.step == SimulationStep.BUYING

    # advance until wrap-around
    for _ in range(5):
        next_step = simulation._next_step_value()
        Human.objects.update(step=next_step.value if hasattr(next_step, "value") else next_step)
        simulation.next_step()

    assert simulation.step == SimulationStep.START_OF_DAY


@pytest.mark.django_db
def test_run_complete_day_advances_day():
    simulation = Simulation.objects.create()

    human = Human.objects.create(step=simulation.step)

    for _ in range(len(Simulation.STEP_SEQUENCE) - 1):
        human.step = simulation._next_step_value().value
        human.save(update_fields=["step"])
        simulation.next_step()

    human.step = simulation._next_step_value().value
    human.save(update_fields=["step"])
    simulation.next_step()

    simulation.refresh_from_db()
    assert simulation.day_number == 1
    assert simulation.step == SimulationStep.START_OF_DAY
