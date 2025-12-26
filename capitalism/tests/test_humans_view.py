import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from capitalism.constants.jobs import Job
from capitalism.constants.simulation_step import SimulationStep
from capitalism.constants.object_type import ObjectType
from capitalism.models import Human, Simulation


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="human_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_humans_view_filters_by_job(logged_client):
    Simulation.objects.create()
    Human.objects.create(job=Job.MINER, dead=False, step=SimulationStep.PRODUCTION)
    Human.objects.create(job=Job.FARMER, dead=False, step=SimulationStep.PRODUCTION)

    response = logged_client.get(reverse("capitalism:humans"), {"job": Job.MINER})

    assert response.status_code == 200
    humans = response.context["humans"]
    assert humans.count() == 1
    assert humans.first().job == Job.MINER


@pytest.mark.django_db
def test_humans_view_filters_by_state(logged_client):
    Simulation.objects.create()
    Human.objects.create(job=Job.MINER, dead=False, step=SimulationStep.PRODUCTION)
    Human.objects.create(job=Job.MINER, dead=True, step=SimulationStep.SELLING)

    response = logged_client.get(reverse("capitalism:humans"), {"state": "dead"})

    assert response.status_code == 200
    humans = response.context["humans"]
    assert humans.count() == 1
    assert humans.first().dead is True


@pytest.mark.django_db
def test_humans_view_shows_selected_human(logged_client):
    Simulation.objects.create()
    human = Human.objects.create(
        name="Test Baker",
        job=Job.BAKER,
        dead=False,
        step=SimulationStep.PRODUCTION,
        money=42,
    )
    human.owned_objects.create(type="bread")
    human.owned_objects.create(type="bread")
    human.owned_objects.create(type="flour")

    response = logged_client.get(reverse("capitalism:humans") + f"?human_id={human.id}")

    assert response.status_code == 200
    selected = response.context["selected_human"]
    summary = response.context["object_summary"]
    assert selected.id == human.id
    assert any(item["label"] == "Bread" and item["quantity"] == 2 for item in summary)


@pytest.mark.django_db
def test_humans_view_filters_by_name(logged_client):
    Simulation.objects.create()
    Human.objects.create(name="Alice Stone", job=Job.MINER, dead=False, step=SimulationStep.PRODUCTION)
    Human.objects.create(name="Bob Doe", job=Job.MINER, dead=False, step=SimulationStep.PRODUCTION)

    response = logged_client.get(reverse("capitalism:humans"), {"name": "Alice"})

    assert response.status_code == 200
    humans = response.context["humans"]
    assert humans.count() == 1
    assert humans.first().name == "Alice Stone"


@pytest.mark.django_db
def test_human_detail_view_exposes_objects(logged_client):
    human = Human.objects.create(
        name="Detail Check",
        job=Job.BAKER,
        money=123,
        age=35,
        dead=False,
        step=SimulationStep.SELLING,
    )
    sale_obj = human.owned_objects.create(type="bread", in_sale=True, price=9.5)
    kept_obj = human.owned_objects.create(type="flour", in_sale=False, price=0)

    response = logged_client.get(reverse("capitalism:human_detail", args=[human.id]))

    assert response.status_code == 200
    assert response.context["human"].id == human.id
    objects = list(response.context["objects"])
    assert sale_obj in objects and kept_obj in objects
    sale_entry = next(obj for obj in objects if obj.id == sale_obj.id)
    assert sale_entry.in_sale is True
    assert sale_entry.price == 9.5
    desired = response.context["desired_object_prices"]
    assert any(item["type"] == ObjectType.BREAD for item in desired)
    selling = response.context["selling_object_prices"]
    assert any(item["type"] == ObjectType.BREAD for item in selling)


@pytest.mark.django_db
def test_humans_view_adds_object_via_post(logged_client):
    Simulation.objects.create()
    human = Human.objects.create(
        name="Post Target",
        job=Job.FARMER,
        dead=False,
        step=SimulationStep.SELLING,
    )

    url = reverse("capitalism:humans") + f"?human_id={human.id}"
    response = logged_client.post(
        url,
        {
            "human_id": str(human.id),
            "object_type": ObjectType.WOOD,
            "quantity": "3",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert human.get_object_quantity(ObjectType.WOOD) == 3
    messages = list(response.context.get("messages", []))
    assert any("ajout" in message.message.lower() for message in messages)


@pytest.mark.django_db
def test_human_detail_view_delete_object(logged_client):
    human = Human.objects.create(
        name="Delete Target",
        job=Job.BAKER,
        dead=False,
        step=SimulationStep.SELLING,
    )
    obj = human.owned_objects.create(type=ObjectType.BREAD)

    response = logged_client.post(
        reverse("capitalism:human_detail", args=[human.id]),
        {
            "action": "delete_objects",
            "object_type": ObjectType.BREAD,
            "quantity": "1",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert human.get_object_quantity(ObjectType.BREAD) == 0
    messages = list(response.context.get("messages", []))
    assert any("supprimé" in message.message.lower() for message in messages)


@pytest.mark.django_db
def test_human_detail_view_add_object(logged_client):
    human = Human.objects.create(
        name="Add Target",
        job=Job.MINER,
        dead=False,
        step=SimulationStep.SELLING,
    )

    response = logged_client.post(
        reverse("capitalism:human_detail", args=[human.id]),
        {
            "action": "add_objects",
            "object_type": ObjectType.ORE,
            "quantity": "2",
        },
        follow=True,
    )

    assert response.status_code == 200
    assert human.get_object_quantity(ObjectType.ORE) == 2
    messages = list(response.context.get("messages", []))
    assert any("ajout" in message.message.lower() for message in messages)


@pytest.mark.django_db
def test_human_detail_view_updates_object_price(logged_client):
    human = Human.objects.create(
        name="Pricer",
        job=Job.MINER,
        dead=False,
        step=SimulationStep.SELLING,
    )
    obj = human.owned_objects.create(type=ObjectType.ORE, price=5.0)

    response = logged_client.post(
        reverse("capitalism:human_detail", args=[human.id]),
        {
            "action": "update_price",
            "object_id": str(obj.id),
            "price": "7.25",
        },
        follow=True,
    )

    assert response.status_code == 200
    obj.refresh_from_db()
    assert obj.price == pytest.approx(7.25)
    assert obj.in_sale is True
    messages = list(response.context.get("messages", []))
    assert any("mis à jour" in message.message.lower() for message in messages)


@pytest.mark.django_db
def test_human_detail_view_can_clear_object_price(logged_client):
    human = Human.objects.create(
        name="Cleaner",
        job=Job.MINER,
        dead=False,
        step=SimulationStep.SELLING,
    )
    obj = human.owned_objects.create(type=ObjectType.ORE, price=5.0)

    response = logged_client.post(
        reverse("capitalism:human_detail", args=[human.id]),
        {
            "action": "update_price",
            "object_id": str(obj.id),
            "price": "",
        },
        follow=True,
    )

    assert response.status_code == 200
    obj.refresh_from_db()
    assert obj.price is None
    assert obj.in_sale is False
    messages = list(response.context.get("messages", []))
    assert any("supprimé" in message.message.lower() for message in messages)
