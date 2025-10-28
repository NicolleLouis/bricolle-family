import pytest

from capitalism.constants.jobs import Job
from capitalism.models import HumanAnalytics


@pytest.mark.django_db
def test_human_analytics_defaults():
    analytics = HumanAnalytics.objects.create()

    assert analytics.job == Job.MINER
    assert analytics.day_number == 0
    assert analytics.number_alive == 0
    assert analytics.average_money == 0.0
    assert analytics.lowest_money == 0
    assert analytics.max_money == 0
    assert analytics.new_joiner == 0
