import pytest

from albion_online.models import PriceRefreshJob
from albion_online import tasks


@pytest.mark.django_db
class TestPriceRefreshTask:
    def test_refresh_price_job_runs_leather_jacket_refresh(self, monkeypatch):
        job = PriceRefreshJob.objects.create(kind=PriceRefreshJob.Kind.LEATHER_JACKET)
        called = {"refresh": False, "invalidate": False}

        class FakeService:
            def refresh_prices(self):
                called["refresh"] = True
                return [object(), object()]

        monkeypatch.setattr(tasks, "LeatherJacketPriceRefreshService", lambda: FakeService())
        monkeypatch.setattr(tasks, "invalidate_leather_jacket_cache", lambda: called.__setitem__("invalidate", True))

        result = tasks.refresh_price_job.run(price_refresh_job_id=job.id, task_id="task-1")

        job.refresh_from_db()
        assert called["refresh"] is True
        assert called["invalidate"] is True
        assert result == {"refreshed_count": 2}
        assert job.status == PriceRefreshJob.Status.SUCCESS
        assert job.refreshed_count == 2
        assert job.task_id == "task-1"

    def test_refresh_price_job_runs_gathering_gear_refresh(self, monkeypatch):
        job = PriceRefreshJob.objects.create(
            kind=PriceRefreshJob.Kind.GATHERING_GEAR,
            context={"resource": "rock"},
        )
        called = {"refresh": None, "invalidate": False}

        class FakeService:
            def refresh_prices(self, selected_resource_filter="all"):
                called["refresh"] = selected_resource_filter
                return [object()]

        monkeypatch.setattr(tasks, "GatheringGearPriceRefreshService", lambda: FakeService())
        monkeypatch.setattr(tasks, "invalidate_gathering_gear_cache", lambda: called.__setitem__("invalidate", True))

        result = tasks.refresh_price_job.run(price_refresh_job_id=job.id, task_id="task-2")

        job.refresh_from_db()
        assert called["refresh"] == "rock"
        assert called["invalidate"] is True
        assert result == {"refreshed_count": 1}
        assert job.status == PriceRefreshJob.Status.SUCCESS
        assert job.refreshed_count == 1
        assert job.task_id == "task-2"

    def test_refresh_price_job_runs_artifact_salvage_refresh(self, monkeypatch):
        job = PriceRefreshJob.objects.create(kind=PriceRefreshJob.Kind.ARTIFACT_SALVAGE)
        called = {"refresh": False, "invalidate": False}

        class FakeService:
            def refresh_prices(self):
                called["refresh"] = True
                return [object(), object(), object()]

        monkeypatch.setattr(tasks, "ArtifactSalvagePriceRefreshService", lambda: FakeService())
        monkeypatch.setattr(
            tasks,
            "invalidate_artifact_salvage_cache",
            lambda: called.__setitem__("invalidate", True),
        )

        result = tasks.refresh_price_job.run(price_refresh_job_id=job.id, task_id="task-3")

        job.refresh_from_db()
        assert called["refresh"] is True
        assert called["invalidate"] is True
        assert result == {"refreshed_count": 3}
        assert job.status == PriceRefreshJob.Status.SUCCESS
        assert job.refreshed_count == 3
        assert job.task_id == "task-3"
