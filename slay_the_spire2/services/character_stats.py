from django.db.models import Count, Q

from slay_the_spire2.models.run_summary import RunSummary


class CharacterStatsService:
    _DEFAULT_SORT_BY = "win_number"
    _DEFAULT_DIRECTION = "desc"
    _ALLOWED_SORT_FIELDS = {
        "character_name",
        "run_number",
        "win_number",
        "win_percentage",
    }

    def get_character_stats(self, sort_by: str | None = None, direction: str | None = None) -> list[dict]:
        rows = (
            RunSummary.objects.filter(character__isnull=False)
            .values("character__name")
            .annotate(
                run_number=Count("id"),
                win_number=Count("id", filter=Q(win=True)),
            )
        )

        stats = []
        for row in rows:
            run_number = row["run_number"]
            win_number = row["win_number"]
            win_percentage = round((win_number / run_number) * 100, 2) if run_number > 0 else 0.0
            stats.append(
                {
                    "character_name": row["character__name"],
                    "run_number": run_number,
                    "win_number": win_number,
                    "win_percentage": win_percentage,
                }
            )

        normalized_sort_by = sort_by if sort_by in self._ALLOWED_SORT_FIELDS else self._DEFAULT_SORT_BY
        normalized_direction = direction if direction in {"asc", "desc"} else self._DEFAULT_DIRECTION
        reverse = normalized_direction == "desc"

        if normalized_sort_by == "character_name":
            return sorted(stats, key=lambda stat: stat["character_name"].lower(), reverse=reverse)
        return sorted(stats, key=lambda stat: stat[normalized_sort_by], reverse=reverse)
