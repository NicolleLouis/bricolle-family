from importlib import import_module

import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestSettingsView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-settings-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_page(self, authenticated_client):
        response = authenticated_client.get(reverse("albion_online:settings"))

        assert response.status_code == 200
        assert b"Settings" in response.content
        assert b"Regenerate Recipes" in response.content
        assert b"mercenary_jacket" in response.content

    def test_post_triggers_recipe_regeneration(self, authenticated_client, monkeypatch):
        settings_view = import_module("albion_online.views.settings_page")
        called = {"refresh": False}

        class FakeService:
            def refresh_recipes(self):
                called["refresh"] = True
                return [object()]

        monkeypatch.setattr(settings_view, "RecipeGenerationService", lambda: FakeService())

        response = authenticated_client.post(reverse("albion_online:settings"))

        assert response.status_code == 302
        assert called["refresh"] is True
