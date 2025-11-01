import pytest

from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.models import Human, HumanAnalytics
from capitalism.services.human_analytics import HumanAnalyticsRecorderService


@pytest.mark.django_db
def test_human_analytics_recorder_populates_per_job_statistics():
    Human.objects.create(
        job=Job.MINER,
        money=200.0,
        age=30,
        step=SimulationStep.ANALYTICS,
    )
    Human.objects.create(
        job=Job.MINER,
        money=100.0,
        age=20,
        step=SimulationStep.ANALYTICS,
    )
    Human.objects.create(
        job=Job.MINER,
        dead=True,
        step=SimulationStep.ANALYTICS,
    )
    Human.objects.create(
        job=Job.BAKER,
        money=50.0,
        age=40,
        step=SimulationStep.ANALYTICS,
    )
    Human.objects.create(
        job=Job.BAKER,
        dead=True,
        step=SimulationStep.ANALYTICS,
    )

    HumanAnalyticsRecorderService(day_number=12).run()

    analytics = HumanAnalytics.objects.filter(day_number=12)
    assert analytics.count() == len(Job.choices)

    miner_stats = analytics.get(job=Job.MINER)
    assert miner_stats.number_alive == 2
    assert miner_stats.dead_number == 1
    assert miner_stats.average_money == pytest.approx(150.0)
    assert miner_stats.lowest_money == 100
    assert miner_stats.max_money == 200
    assert miner_stats.average_age == pytest.approx(25.0)
    assert miner_stats.new_joiner == 0

    baker_stats = analytics.get(job=Job.BAKER)
    assert baker_stats.number_alive == 1
    assert baker_stats.dead_number == 1
    assert baker_stats.average_money == pytest.approx(50.0)
    assert baker_stats.lowest_money == 50
    assert baker_stats.max_money == 50
    assert baker_stats.average_age == pytest.approx(40.0)

    lumberjack_stats = analytics.get(job=Job.LUMBERJACK)
    assert lumberjack_stats.number_alive == 0
    assert lumberjack_stats.dead_number == 0
    assert lumberjack_stats.average_money == pytest.approx(0.0)
    assert lumberjack_stats.lowest_money == 0
    assert lumberjack_stats.max_money == 0
    assert lumberjack_stats.average_age == pytest.approx(0.0)
