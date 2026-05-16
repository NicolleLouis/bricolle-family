import pytest
from django.contrib import admin
from django.utils import timezone

from albion_online.models import AodpRequestLog
from albion_online.models.aodp_request_log import AodpRequestLogAdmin


@pytest.mark.django_db
class TestAodpRequestLogModel:
    def test_create_log_and_string_representation(self):
        log = AodpRequestLog.objects.create(
            source="leather_jacket",
            request_url="https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json?locations=Bridgewatch",
            request_query_string="locations=Bridgewatch",
            response_status_code=200,
            response_body_raw="[]",
            duration_ms=42,
            created_at=timezone.now(),
        )

        assert str(log) == (
            "leather_jacket - https://europe.albion-online-data.com/api/v2/stats/prices/T4_BAG.json?locations=Bridgewatch"
        )
        assert log.is_error is False
        assert log.response_status_code == 200
        assert log.duration_ms == 42

    def test_logs_order_newest_first(self):
        older_log = AodpRequestLog.objects.create(
            source="artifact_salvage",
            request_url="https://example.com/older",
            request_query_string="older=1",
            response_body_raw="[]",
            created_at=timezone.now(),
        )
        newer_log = AodpRequestLog.objects.create(
            source="gathering_gear",
            request_url="https://example.com/newer",
            request_query_string="newer=1",
            response_body_raw="[]",
            created_at=timezone.now(),
        )

        ordered_logs = list(AodpRequestLog.objects.values_list("id", flat=True))

        assert ordered_logs[0] == newer_log.id
        assert ordered_logs[1] == older_log.id

    def test_model_is_registered_in_admin(self):
        assert isinstance(admin.site._registry[AodpRequestLog], AodpRequestLogAdmin)
        assert admin.site._registry[AodpRequestLog].search_fields == (
            "source",
            "request_url",
            "request_query_string",
            "response_body_raw",
            "error_message",
        )
