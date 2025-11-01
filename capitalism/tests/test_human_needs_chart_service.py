import pytest

from capitalism.models import Human
from capitalism.services.human_analytics import HumanNeedsSatisfactionChartService


@pytest.mark.django_db
def test_human_needs_chart_counts_only_humans_with_age():
    Human.objects.create(age=0, time_since_need_fulfilled=0)
    Human.objects.create(age=3, time_since_need_fulfilled=0)
    Human.objects.create(age=5, time_since_need_fulfilled=2)

    html = HumanNeedsSatisfactionChartService().render()

    assert "Needs Met" in html
    assert "Needs Unmet" in html
