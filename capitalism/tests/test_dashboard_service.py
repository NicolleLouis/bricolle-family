import pytest

from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, Simulation
from capitalism.services.dashboard import DashboardService


@pytest.mark.django_db
def test_macro_overview_without_simulation():
    Human.objects.create()

    info = DashboardService().macro_overview()

    assert info["has_simulation"] is False
    assert info["day_number"] is None
    assert info["step"] is None
    assert info["step_label"] is None
    assert info["alive_humans"] == 1


@pytest.mark.django_db
def test_macro_overview_with_simulation():
    simulation = Simulation.objects.create(
        day_number=4,
        step=SimulationStep.CONSUMPTION,
    )
    Human.objects.create(dead=False)
    Human.objects.create(dead=True)

    info = DashboardService().macro_overview()

    assert info["has_simulation"] is True
    assert info["day_number"] == 4
    assert info["step"] == simulation.step
    assert info["step_label"] == SimulationStep.CONSUMPTION.label
    assert info["alive_humans"] == 1
