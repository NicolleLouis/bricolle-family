import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from documents.constants.directories import Directories
from documents.models import Document


@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="capitalism_ideas_viewer",
        password="password",
        is_staff=True,
    )


@pytest.fixture
def logged_client(client, user):
    client.force_login(user)
    return client


@pytest.mark.django_db
def test_capitalism_idea_page_renders_document(logged_client):
    response = logged_client.get(reverse("capitalism:idea"))

    assert response.status_code == 200
    document = Document.objects.get(
        title="Simulation Ideas",
        directory=Directories.CAPITALISM,
    )
    assert response.context["document"] == document
