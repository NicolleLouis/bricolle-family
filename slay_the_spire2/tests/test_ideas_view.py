import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from documents.constants.directories import Directories
from documents.models import Document


@pytest.mark.django_db
class TestIdeasView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="ideas-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_ideas_view_renders_document_page(self, authenticated_client):
        response = authenticated_client.get(reverse("slay_the_spire2:ideas"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "<h1>Ideas</h1>" in page_content
        assert "Edit" in page_content
        assert Document.objects.filter(title="Ideas", directory=Directories.STS).exists()
