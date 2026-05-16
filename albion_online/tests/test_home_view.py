import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestHomeView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_home_get_returns_page(self, authenticated_client):
        response = authenticated_client.get(reverse("albion_online:home"))

        assert response.status_code == 200
        assert b"Albion Online" in response.content
        assert b"Leather Jacket" in response.content
        assert b"Artifact Salvage" in response.content
        assert b"Gathering Gear" in response.content
        assert b"AODP Logs" in response.content
        assert reverse("albion_online:leather_jacket").encode() in response.content
        assert reverse("albion_online:artifact_salvage").encode() in response.content
        assert reverse("albion_online:gathering_gear").encode() in response.content
        assert reverse("albion_online:aodp_request_log").encode() in response.content
