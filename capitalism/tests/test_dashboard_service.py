import pytest

from capitalism.models import Human, Simulation
from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.services.dashboard import DashboardService


@pytest.mark.django_db
def test_macro_overview_includes_total_money_without_simulation():
    Human.objects.bulk_create(
        [
            Human(job=Job.BAKER, money=25, dead=False),
            Human(job=Job.MINER, money=30, dead=False),
            Human(job=Job.FARMER, money=10, dead=True),
        ]
    )

    data = DashboardService().macro_overview()

    assert data["has_simulation"] is False
    assert data["alive_humans"] == 2
    assert data["total_money"] == pytest.approx(55.0)


@pytest.mark.django_db
def test_macro_overview_total_money_with_simulation():
    simulation = Simulation.objects.create(step=SimulationStep.START_OF_DAY, day_number=3)
    Human.objects.bulk_create(
        [
            Human(job=Job.BAKER, money=40, dead=False),
            Human(job=Job.MINER, money=12.5, dead=False),
        ]
    )

    data = DashboardService().macro_overview()

    assert data["has_simulation"] is True
    assert data["day_number"] == simulation.day_number
    assert data["total_money"] == pytest.approx(52.5)
