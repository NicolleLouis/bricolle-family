from django.db.models import Count

from slay_the_spire2.models.run_summary import RunSummary


class DeathTypeStatsService:
    def get_death_type_stats(self) -> list[dict]:
        rows = (
            RunSummary.objects.filter(killed_by__isnull=False)
            .values("killed_by__name", "killed_by__type")
            .annotate(death_count=Count("id"))
            .filter(death_count__gte=1)
            .order_by("-death_count", "killed_by__name")
        )

        return [
            {
                "encounter_name": row["killed_by__name"],
                "encounter_type": row["killed_by__type"],
                "death_count": row["death_count"],
            }
            for row in rows
        ]
