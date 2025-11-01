import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, MarketPerceivedPrice
from capitalism.services.pricing import MarketPerceivedPriceResetService


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="objects_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_objects_view_exposes_statistics(logged_client):
    owner = Human.objects.create(name="Viewer Human")
    owner.owned_objects.create(type=ObjectType.WOOD, price=5.0, in_sale=True)
    owner.owned_objects.create(type=ObjectType.WOOD, price=10.0, in_sale=True)
    MarketPerceivedPriceResetService(day_number=0).reset()
    MarketPerceivedPrice.objects.filter(object=ObjectType.WOOD).update(perceived_price=8.5)

    response = logged_client.get(reverse("capitalism:objects"))

    assert response.status_code == 200
    stats = {entry["type"]: entry for entry in response.context["stats"]}
    wood_stats = stats[ObjectType.WOOD]
    assert wood_stats["quantity"] == 2
    assert wood_stats["perceived_price"] == pytest.approx(8.5)
