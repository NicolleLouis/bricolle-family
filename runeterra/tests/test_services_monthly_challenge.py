import pytest

from runeterra.models import Champion
from runeterra.services.monthly_challenge import (
    MonthlyChallengeAvailableService,
    MonthlyChallengeConsumeService,
    MonthlyChallengeResetService,
)


@pytest.mark.django_db
def test_reset_monthly_challenge_sets_monthly_try_remaining_to_three():
    Champion.objects.create(
        name="Ashe",
        primary_region="FRELJORD",
        star_level=2,
        monthly_try_remaining=0,
    )
    Champion.objects.create(
        name="Garen",
        primary_region="DEMACIA",
        star_level=3,
        monthly_try_remaining=1,
    )
    Champion.objects.create(
        name="Jinx",
        primary_region="PILTOVER_ZAUN",
        star_level=1,
        monthly_try_remaining=3,
    )

    updated = MonthlyChallengeResetService().reset()

    assert updated == 3
    assert Champion.objects.filter(monthly_try_remaining=3).count() == 3


@pytest.mark.django_db
def test_monthly_challenge_available_service_filters_and_counts():
    Champion.objects.create(
        name="Ashe",
        primary_region="FRELJORD",
        star_level=2,
        monthly_try_remaining=1,
    )
    Champion.objects.create(
        name="Garen",
        primary_region="DEMACIA",
        star_level=3,
        monthly_try_remaining=2,
    )
    Champion.objects.create(
        name="Teemo",
        primary_region="BANDLE",
        star_level=2,
        monthly_try_remaining=0,
    )
    Champion.objects.create(
        name="Lux",
        primary_region="DEMACIA",
        star_level=1,
        monthly_try_remaining=3,
    )

    champions, counts, total = MonthlyChallengeAvailableService().list_available()

    assert total == 2
    assert counts[2] == 1
    assert counts[3] == 1
    assert all(counts[star] == 0 for star in range(4, 8))
    assert list(champions.values_list("name", flat=True)) == ["Ashe", "Garen"]

    champions, counts, total = MonthlyChallengeAvailableService().list_available(3)

    assert total == 2
    assert list(champions.values_list("name", flat=True)) == ["Garen"]


@pytest.mark.django_db
def test_monthly_challenge_consume_service_decrements():
    champion = Champion.objects.create(
        name="Ashe",
        primary_region="FRELJORD",
        star_level=2,
        monthly_try_remaining=1,
    )

    updated = MonthlyChallengeConsumeService().consume(champion.id)

    champion.refresh_from_db()
    assert updated is True
    assert champion.monthly_try_remaining == 0
