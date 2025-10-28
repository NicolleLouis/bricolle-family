import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.jobs import Job
from capitalism.models import Human


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
def test_human_analytics_view_returns_job_stats(logged_client):
    Human.objects.create(job=Job.FARMER, money=80)
    Human.objects.create(job=Job.FARMER, money=120)

    response = logged_client.get(reverse("capitalism:human_analytics"))

    assert response.status_code == 200
    stats = {entry["job"]: entry for entry in response.context["stats"]}
    farmer_stats = stats[Job.FARMER]
    assert farmer_stats["count"] == 2
    assert farmer_stats["max_money"] == pytest.approx(120)
