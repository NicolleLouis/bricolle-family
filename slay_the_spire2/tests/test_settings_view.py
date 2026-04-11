from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse


@pytest.mark.django_db
class TestSettingsView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="test-admin-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_settings_get_returns_page(self, authenticated_client):
        response = authenticated_client.get(reverse("slay_the_spire2:settings"))

        assert response.status_code == 200
        assert b"Relancer le parse global" in response.content

    @patch("slay_the_spire2.views.settings.reparse_all_run_files.delay")
    def test_settings_post_enqueues_async_reparse(self, mocked_delay, authenticated_client):
        response = authenticated_client.post(reverse("slay_the_spire2:settings"))

        assert response.status_code == 302
        assert response.url == reverse("slay_the_spire2:settings")
        mocked_delay.assert_called_once_with()
