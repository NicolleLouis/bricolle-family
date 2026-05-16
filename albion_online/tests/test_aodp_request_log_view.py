import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from albion_online.models import AodpRequestLog


@pytest.mark.django_db
class TestAodpRequestLogView:
    @pytest.fixture
    def authenticated_client(self, client):
        user = User.objects.create_user(
            username="albion-online-aodp-log-user",
            password="test-password",
            is_staff=True,
            is_superuser=True,
        )
        client.force_login(user)
        return client

    def test_get_returns_page_and_displays_logs(self, authenticated_client):
        AodpRequestLog.objects.create(
            source="price_fetcher",
            request_url="https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json",
            request_query_string="locations=Bridgewatch",
            response_status_code=200,
            response_body_raw='{"item_id":"T4_BAG"}',
            duration_ms=17,
        )
        AodpRequestLog.objects.create(
            source="price_fetcher",
            request_url="https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json",
            request_query_string="locations=Martlock",
            response_status_code=500,
            response_body_raw='{"detail":"boom"}',
            error_message="500 Server Error",
            is_error=True,
            duration_ms=23,
        )

        response = authenticated_client.get(reverse("albion_online:aodp_request_log"))

        assert response.status_code == 200
        assert b"AODP request logs" in response.content
        assert b"locations=Bridgewatch" in response.content
        assert b"locations=Martlock" in response.content
        assert b"500 Server Error" in response.content
        assert b"table-danger" in response.content

    def test_get_filters_logs_by_search_string(self, authenticated_client):
        AodpRequestLog.objects.create(
            source="price_fetcher",
            request_url="https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json",
            request_query_string="locations=Bridgewatch",
            response_status_code=200,
            response_body_raw='{"item_id":"T4_BAG"}',
            duration_ms=17,
        )
        AodpRequestLog.objects.create(
            source="price_fetcher",
            request_url="https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json",
            request_query_string="locations=Martlock",
            response_status_code=500,
            response_body_raw='{"detail":"boom"}',
            error_message="500 Server Error",
            is_error=True,
            duration_ms=23,
        )

        response = authenticated_client.get(
            f"{reverse('albion_online:aodp_request_log')}?q=Martlock"
        )

        assert response.status_code == 200
        assert b"locations=Martlock" in response.content
        assert b"locations=Bridgewatch" not in response.content
        assert b"500 Server Error" in response.content
