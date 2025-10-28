import pytest

from capitalism.constants.jobs import Job
from capitalism.models import Human
from capitalism.services.human_analytics import HumanJobAnalyticsService


@pytest.mark.django_db
def test_human_job_analytics_counts_and_money_ranges():
    Human.objects.create(job=Job.MINER, money=100)
    Human.objects.create(job=Job.MINER, money=200)
    Human.objects.create(job=Job.BAKER, money=50)

    stats = HumanJobAnalyticsService().run()
    stats_map = {entry["job"]: entry for entry in stats}

    miner_stats = stats_map[Job.MINER]
    assert miner_stats["count"] == 2
    assert miner_stats["min_money"] == pytest.approx(100)
    assert miner_stats["avg_money"] == pytest.approx(150)
    assert miner_stats["max_money"] == pytest.approx(200)

    baker_stats = stats_map[Job.BAKER]
    assert baker_stats["count"] == 1
    assert baker_stats["min_money"] == pytest.approx(50)
    assert baker_stats["avg_money"] == pytest.approx(50)
    assert baker_stats["max_money"] == pytest.approx(50)

    lumberjack_stats = stats_map[Job.LUMBERJACK]
    assert lumberjack_stats["count"] == 0
    assert lumberjack_stats["min_money"] is None
