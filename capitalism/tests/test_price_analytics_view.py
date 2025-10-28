import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.object_type import ObjectType
from capitalism.models import PriceAnalytics


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="price_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_price_analytics_view_filters_by_object(logged_client):
    PriceAnalytics.objects.bulk_create(
        [
            PriceAnalytics(
                day_number=day,
                object_type=ObjectType.WOOD,
                lowest_price_displayed=1 + day,
                max_price_displayed=5 + day,
                average_price_displayed=3 + day,
                lowest_price=1 + day,
                max_price=5 + day,
                average_price=3 + day,
            )
            for day in range(3)
        ]
    )

    response = logged_client.get(reverse("capitalism:price_analytics"), {"object": ObjectType.WOOD})

    assert response.status_code == 200
    analytics = response.context["analytics"]
    assert len(analytics) == 3
    assert analytics[0].day_number == 0
    assert response.context["selected_object"] == ObjectType.WOOD


@pytest.mark.django_db
def test_price_analytics_view_defaults_when_invalid_object(logged_client):
    response = logged_client.get(reverse("capitalism:price_analytics"), {"object": "unknown"})

    assert response.status_code == 200
    assert response.context["selected_object"] in dict(ObjectType.choices)
