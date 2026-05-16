from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from albion_online.models import AodpRequestLog


class AodpRequestLogService:
    RETENTION_WINDOW = timedelta(hours=24)

    def list_logs(self, search_string: str | None = None, source: str | None = None, limit: int | None = 200):
        query = AodpRequestLog.objects.all()
        normalized_source = source.strip() if source else ""
        normalized_search_string = search_string.strip() if search_string else ""
        if normalized_source:
            query = query.filter(source=normalized_source)
        if normalized_search_string:
            query = query.filter(
                Q(request_query_string__icontains=normalized_search_string)
                | Q(response_body_raw__icontains=normalized_search_string)
            )
        if limit is not None:
            query = query[:limit]
        return query

    def purge_expired(self, current_time=None) -> int:
        reference_time = current_time or timezone.now()
        cutoff = reference_time - self.RETENTION_WINDOW
        deleted_count, _ = AodpRequestLog.objects.filter(created_at__lt=cutoff).delete()
        return deleted_count

    def _create_log(
        self,
        *,
        source: str,
        request_url: str,
        request_query_string: str,
        response_status_code: int | None,
        response_body_raw: str,
        error_message: str = "",
        is_error: bool = False,
        duration_ms: int | None = None,
    ) -> AodpRequestLog:
        return AodpRequestLog.objects.create(
            source=source,
            request_url=request_url,
            request_query_string=request_query_string,
            response_status_code=response_status_code,
            response_body_raw=response_body_raw,
            error_message=error_message,
            is_error=is_error,
            duration_ms=duration_ms,
        )
