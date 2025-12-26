import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.object_type import ObjectType
from capitalism.models import (
    Human,
    HumanAnalytics,
    MarketPerceivedPrice,
    ObjectStack,
    Simulation,
    Transaction,
)
from capitalism.services.pricing import GlobalPriceReferenceService


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="tester",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_start_simulation_creates_if_missing(logged_client):
    response = logged_client.post(reverse("capitalism:settings"), {"action": "start"}, follow=True)

    assert response.status_code == 200
    assert Simulation.objects.count() == 1


@pytest.mark.django_db
def test_reset_simulation_clears_data(logged_client):
    simulation = Simulation.objects.create()
    human = Human.objects.create(step=simulation.step)
    ObjectStack.objects.create(owner=human)
    HumanAnalytics.objects.create()
    Transaction.objects.create(object_type=ObjectType.ORE, price=10)
    MarketPerceivedPrice.objects.create(updated_at=99, object=ObjectType.ORE, perceived_price=42.0)

    response = logged_client.post(
        reverse("capitalism:settings"),
        {"action": "reset"},
        follow=True,
    )

    assert response.status_code == 200
    assert Simulation.objects.count() == 1
    assert Human.objects.count() == 0
    assert ObjectStack.objects.count() == 0
    assert HumanAnalytics.objects.count() == 0
    assert Transaction.objects.count() == 0
    assert MarketPerceivedPrice.objects.count() == len(ObjectType.choices)

    reference = GlobalPriceReferenceService()
    for object_type, _label in ObjectType.choices:
        perceived = MarketPerceivedPrice.objects.get(object=object_type)
        assert perceived.updated_at == 0
        assert perceived.perceived_price == pytest.approx(
            reference.get_reference_price(object_type)
        )


@pytest.mark.django_db
def test_generate_humans_requires_start_of_day(logged_client):
    simulation = Simulation.objects.create(step="production")

    response = logged_client.post(
        reverse("capitalism:settings"),
        {"action": "generate", "count_miner": "2"},
        follow=True,
    )

    assert response.status_code == 200
    assert Human.objects.count() == 0
    assert Simulation.objects.get(pk=simulation.pk).step == "production"


@pytest.mark.django_db
def test_generate_humans_creates_per_job(logged_client):
    Simulation.objects.create(step="start_of_day")

    payload = {
        "action": "generate",
        "count_miner": "2",
        "count_farmer": "1",
        "count_baker": "0",
    }

    response = logged_client.post(reverse("capitalism:settings"), payload, follow=True)

    assert response.status_code == 200
    assert Human.objects.filter(job="miner").count() == 2
    assert Human.objects.filter(job="farmer").count() == 1
    assert Human.objects.filter(job="baker").count() == 0
    assert all(h.name for h in Human.objects.all())
    assert Human.objects.filter(dead=True).count() == 0
