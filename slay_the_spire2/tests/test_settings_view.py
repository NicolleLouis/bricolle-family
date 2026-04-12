from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from slay_the_spire2.models.reparse_run_job import ReparseRunJob


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
        assert b"Aucun run du job pour le moment." in response.content

    @patch("slay_the_spire2.views.settings.reparse_all_run_files.delay")
    def test_settings_post_enqueues_async_reparse(self, mocked_delay, authenticated_client):
        response = authenticated_client.post(reverse("slay_the_spire2:settings"))

        assert response.status_code == 302
        assert response.url == reverse("slay_the_spire2:settings")
        reparse_run_job = ReparseRunJob.objects.get()
        mocked_delay.assert_called_once_with(reparse_run_job_id=reparse_run_job.id)
        assert reparse_run_job.status == ReparseRunJob.Status.QUEUED

    def test_settings_get_displays_last_reparse_job_recap(self, authenticated_client):
        ReparseRunJob.objects.create(
            status=ReparseRunJob.Status.SUCCESS,
            reparsed_count=12,
            error_count=3,
        )

        response = authenticated_client.get(reverse("slay_the_spire2:settings"))

        assert response.status_code == 200
        page_content = response.content.decode("utf-8")
        assert "Dernier run du job" in page_content
        assert "Success" in page_content
        assert ">12<" in page_content
        assert ">3<" in page_content
