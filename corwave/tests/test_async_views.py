from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from corwave.models import CorwaveEnrichmentJob


@pytest.mark.django_db
class TestCorwaveAsyncViews:
    @staticmethod
    def _create_staff_user():
        return get_user_model().objects.create_user(
            username="tester",
            password="secret",
            is_staff=True,
        )

    def test_home_post_creates_job_and_enqueues_task(self, client, settings, tmp_path):
        settings.MEDIA_ROOT = str(tmp_path)
        user = self._create_staff_user()
        client.force_login(user)

        csv_file = SimpleUploadedFile(
            "pubmed.csv",
            b"Title,Abstract\nA,a\nB,b\n",
            content_type="text/csv",
        )

        with patch("corwave.views.home.run_corwave_enrichment_job.delay") as mocked_delay:
            response = client.post(reverse("corwave:home"), {"csv_file": csv_file})

        assert response.status_code == 200
        assert b"Calcul fini dans 4 secondes" in response.content
        job = CorwaveEnrichmentJob.objects.get()
        mocked_delay.assert_called_once_with(job.id)

    def test_job_status_returns_download_url_when_done(self, client):
        user = self._create_staff_user()
        client.force_login(user)
        job = CorwaveEnrichmentJob.objects.create(
            status=CorwaveEnrichmentJob.Status.DONE,
            input_file_name="pubmed.csv",
            total_rows=1,
            processed_rows=1,
        )
        job.output_file.save(
            "result.csv",
            ContentFile("Title,Abstract,article_type\nA,a,Review\n".encode("utf-8")),
            save=True,
        )

        response = client.get(reverse("corwave:job_status", args=[job.id]))

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "done"
        assert payload["download_url"].endswith(f"/corwave/jobs/{job.id}/download")

    def test_job_download_returns_csv_when_done(self, client):
        user = self._create_staff_user()
        client.force_login(user)
        job = CorwaveEnrichmentJob.objects.create(
            status=CorwaveEnrichmentJob.Status.DONE,
            input_file_name="pubmed.csv",
            total_rows=1,
            processed_rows=1,
        )
        job.output_file.save(
            "result.csv",
            ContentFile("Title,Abstract,article_type\nA,a,Review\n".encode("utf-8")),
            save=True,
        )

        response = client.get(reverse("corwave:job_download", args=[job.id]))

        assert response.status_code == 200
        assert "text/csv" in response["Content-Type"]

    def test_job_download_returns_409_when_file_is_not_ready(self, client):
        user = self._create_staff_user()
        client.force_login(user)
        job = CorwaveEnrichmentJob.objects.create(
            status=CorwaveEnrichmentJob.Status.PROCESSING,
            input_file_name="pubmed.csv",
            total_rows=1,
            processed_rows=0,
        )

        response = client.get(reverse("corwave:job_download", args=[job.id]))

        assert response.status_code == 409
