from datetime import timedelta

import pytest
from django.utils import timezone

from albion_online.models import AodpRequestLog
from albion_online.services.aodp_request_log_service import AodpRequestLogService


@pytest.mark.django_db
class TestAodpRequestLogService:
    def test_list_logs_searches_query_string_and_body(self):
        matching_query_log = AodpRequestLog.objects.create(
            source="leather_jacket",
            request_url="https://example.com/query",
            request_query_string="locations=Bridgewatch",
            response_body_raw='{"data": "no match"}',
        )
        matching_body_log = AodpRequestLog.objects.create(
            source="gathering_gear",
            request_url="https://example.com/body",
            request_query_string="locations=Martlock",
            response_body_raw='{"message": "valuable result"}',
        )
        AodpRequestLog.objects.create(
            source="artifact_salvage",
            request_url="https://example.com/other",
            request_query_string="locations=Lymhurst",
            response_body_raw='{"message": "ignored"}',
        )

        service = AodpRequestLogService()

        query_results = list(service.list_logs(search_string="Bridgewatch"))
        body_results = list(service.list_logs(search_string="valuable"))

        assert query_results == [matching_query_log]
        assert body_results == [matching_body_log]

    def test_list_logs_can_filter_by_source(self):
        expected_log = AodpRequestLog.objects.create(
            source="artifact_salvage",
            request_url="https://example.com/expected",
            request_query_string="locations=Fort Sterling",
            response_body_raw="[]",
        )
        AodpRequestLog.objects.create(
            source="leather_jacket",
            request_url="https://example.com/other",
            request_query_string="locations=Bridgewatch",
            response_body_raw="[]",
        )

        service = AodpRequestLogService()

        results = list(service.list_logs(source="artifact_salvage"))

        assert results == [expected_log]

    def test_purge_expired_removes_only_logs_older_than_twenty_four_hours(self):
        recent_log = AodpRequestLog.objects.create(
            source="leather_jacket",
            request_url="https://example.com/recent",
            request_query_string="locations=Bridgewatch",
            response_body_raw="[]",
        )
        expired_log = AodpRequestLog.objects.create(
            source="gathering_gear",
            request_url="https://example.com/expired",
            request_query_string="locations=Martlock",
            response_body_raw="[]",
        )

        cutoff_time = timezone.now() - timedelta(days=2)
        AodpRequestLog.objects.filter(id=expired_log.id).update(created_at=cutoff_time)

        deleted_count = AodpRequestLogService().purge_expired(current_time=timezone.now())

        assert deleted_count == 1
        assert list(AodpRequestLog.objects.values_list("id", flat=True)) == [recent_log.id]
