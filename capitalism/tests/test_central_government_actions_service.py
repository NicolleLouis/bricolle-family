import pytest

from capitalism.constants.jobs import Job
from capitalism.models import CentralGovernment, Human, HumanAnalytics, Simulation
from capitalism.services.central_government_actions import CentralGovernmentActionsService


@pytest.mark.django_db
def test_central_government_actions_distributes_money_to_target_job():
    simulation = Simulation.objects.create()
    central_government, _ = CentralGovernment.objects.get_or_create(
        simulation=simulation,
        defaults={"money": 90.0},
    )
    if central_government.money != 90.0:
        central_government.money = 90.0
        central_government.save(update_fields=["money"])

    HumanAnalytics.objects.create(
        day_number=simulation.day_number,
        job=Job.MINER,
        number_alive=2,
        average_money=25.0,
    )
    HumanAnalytics.objects.create(
        day_number=simulation.day_number,
        job=Job.BAKER,
        number_alive=1,
        average_money=50.0,
    )

    first_human = Human.objects.create(money=10.0, job=Job.MINER)
    second_human = Human.objects.create(money=20.0, job=Job.MINER)
    other_human = Human.objects.create(money=30.0, job=Job.BAKER)

    CentralGovernmentActionsService(simulation).run()

    first_human.refresh_from_db()
    second_human.refresh_from_db()
    other_human.refresh_from_db()
    central_government.refresh_from_db()

    assert first_human.money == pytest.approx(55.0)
    assert second_human.money == pytest.approx(65.0)
    assert other_human.money == pytest.approx(30.0)
    assert central_government.money == pytest.approx(0.0)
