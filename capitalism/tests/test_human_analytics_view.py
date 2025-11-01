import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.jobs import Job
from capitalism.models import Human, HumanAnalytics


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="analytics_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_human_repartition_view_returns_job_stats(logged_client):
    Human.objects.create(job=Job.FARMER, money=80)
    Human.objects.create(job=Job.FARMER, money=120)

    response = logged_client.get(reverse("capitalism:human_repartition"))

    assert response.status_code == 200
    stats = {entry["job"]: entry for entry in response.context["stats"]}
    farmer_stats = stats[Job.FARMER]
    assert farmer_stats["count"] == 2
    assert farmer_stats["max_money"] == pytest.approx(120)


@pytest.mark.django_db
def test_human_analytics_view_filters_by_job(logged_client):
    HumanAnalytics.objects.create(
        day_number=1,
        job=Job.MINER,
        number_alive=3,
        average_money=150.0,
        lowest_money=100,
        max_money=200,
        dead_number=1,
        average_age=32.5,
    )
    HumanAnalytics.objects.create(
        day_number=2,
        job=Job.MINER,
        number_alive=4,
        average_money=180.0,
        lowest_money=90,
        max_money=250,
        dead_number=0,
        average_age=33.5,
    )
    HumanAnalytics.objects.create(
        day_number=1,
        job=Job.BAKER,
        number_alive=2,
        average_money=90.0,
        lowest_money=60,
        max_money=120,
        dead_number=0,
        average_age=29.0,
    )

    response = logged_client.get(
        reverse("capitalism:human_analytics"), {"job": Job.MINER}
    )

    assert response.status_code == 200
    assert response.context["selected_job"] == Job.MINER
    assert response.context["job_label"] == Job.MINER.label
    analytics = list(response.context["analytics"])
    assert [entry.day_number for entry in analytics] == [1, 2]
    assert all(entry.job == Job.MINER for entry in analytics)


@pytest.mark.django_db
def test_human_analytics_view_falls_back_to_default_job(logged_client):
    HumanAnalytics.objects.create(
        day_number=1,
        job=Job.MINER,
        number_alive=5,
        average_money=120.0,
        lowest_money=75,
        max_money=180,
        dead_number=0,
        average_age=31.2,
    )

    response = logged_client.get(
        reverse("capitalism:human_analytics"), {"job": "unknown"}
    )

    assert response.status_code == 200
    assert response.context["selected_job"] == Job.MINER
    analytics = list(response.context["analytics"])
    assert len(analytics) == 1
    assert analytics[0].job == Job.MINER
