import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.object_type import ObjectType
from capitalism.models import Transaction


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="transactions_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_transactions_view_lists_transactions(logged_client):
    Transaction.objects.create(object_type=ObjectType.WOOD, price=5)
    Transaction.objects.create(object_type=ObjectType.BREAD, price=7)

    response = logged_client.get(reverse("capitalism:transactions"))

    assert response.status_code == 200
    transactions = response.context["transactions"]
    assert transactions.count() == 2


@pytest.mark.django_db
def test_transactions_view_filters_by_object_type(logged_client):
    Transaction.objects.create(object_type=ObjectType.WOOD, price=5)
    bread_tx = Transaction.objects.create(object_type=ObjectType.BREAD, price=7)

    response = logged_client.get(
        reverse("capitalism:transactions"),
        {"object_type": ObjectType.BREAD},
    )

    assert response.status_code == 200
    transactions = list(response.context["transactions"])
    assert transactions == [bread_tx]
    assert response.context["selected_object_type"] == ObjectType.BREAD
