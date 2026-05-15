import logging

from celery import shared_task

from albion_online.models import PriceRefreshJob
from albion_online.services.artifact_salvage_price_refresh import ArtifactSalvagePriceRefreshService
from albion_online.services.gathering_gear_price_refresh import GatheringGearPriceRefreshService
from albion_online.services.mercenary_jacket_price_refresh import LeatherJacketPriceRefreshService
from albion_online.services.price_refresh_cache import (
    invalidate_artifact_salvage_cache,
    invalidate_gathering_gear_cache,
    invalidate_leather_jacket_cache,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def refresh_price_job(self, price_refresh_job_id: int, task_id: str | None = None) -> dict:
    price_refresh_job = PriceRefreshJob.objects.get(id=price_refresh_job_id)
    effective_task_id = task_id or getattr(getattr(self, "request", None), "id", "")
    price_refresh_job.mark_running(effective_task_id)

    try:
        if price_refresh_job.kind == PriceRefreshJob.Kind.LEATHER_JACKET:
            created_prices = LeatherJacketPriceRefreshService().refresh_prices()
            invalidate_leather_jacket_cache()
        elif price_refresh_job.kind == PriceRefreshJob.Kind.GATHERING_GEAR:
            selected_resource_filter = price_refresh_job.context.get("resource", "ore")
            created_prices = GatheringGearPriceRefreshService().refresh_prices(
                selected_resource_filter=selected_resource_filter
            )
            invalidate_gathering_gear_cache()
        elif price_refresh_job.kind == PriceRefreshJob.Kind.ARTIFACT_SALVAGE:
            created_prices = ArtifactSalvagePriceRefreshService().refresh_prices()
            invalidate_artifact_salvage_cache()
        else:
            raise ValueError(f"Unknown price refresh job kind: {price_refresh_job.kind}")
    except Exception as error:
        price_refresh_job.mark_failed(str(error))
        logger.exception("Albion Online price refresh task failed.")
        raise

    price_refresh_job.mark_success(len(created_prices))
    return {"refreshed_count": len(created_prices)}
