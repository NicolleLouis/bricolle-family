from django.db.models import Count, Q
import plotly.express as px

from slay_the_spire2.models.relic import Relic
from slay_the_spire2.models.run_summary import RunSummary


class RelicStatsService:
    _DEFAULT_SORT_BY = "win_number"
    _DEFAULT_DIRECTION = "desc"
    _ALLOWED_SORT_FIELDS = {
        "relic_name",
        "run_number",
        "win_number",
        "win_percentage",
    }

    def get_relic_stats(
        self,
        sort_by: str | None = None,
        direction: str | None = None,
        character_id: int | None = None,
    ) -> list[dict]:
        character_filter = Q()
        if character_id is not None:
            character_filter = Q(run_summaries__character_id=character_id)

        rows = Relic.objects.annotate(
            run_number=Count("run_summaries", filter=character_filter, distinct=True),
            win_number=Count(
                "run_summaries",
                filter=Q(run_summaries__win=True) & character_filter,
                distinct=True,
            ),
        ).filter(run_number__gt=0)

        stats = []
        for row in rows:
            run_number = row.run_number
            win_number = row.win_number
            win_percentage = round((win_number / run_number) * 100, 2) if run_number > 0 else 0.0
            stats.append(
                {
                    "relic_name": row.name,
                    "run_number": run_number,
                    "win_number": win_number,
                    "win_percentage": win_percentage,
                }
            )

        normalized_sort_by = sort_by if sort_by in self._ALLOWED_SORT_FIELDS else self._DEFAULT_SORT_BY
        normalized_direction = direction if direction in {"asc", "desc"} else self._DEFAULT_DIRECTION
        reverse = normalized_direction == "desc"

        if normalized_sort_by == "relic_name":
            return sorted(stats, key=lambda stat: stat["relic_name"].lower(), reverse=reverse)
        return sorted(stats, key=lambda stat: stat[normalized_sort_by], reverse=reverse)

    def get_win_by_relic_number_chart(self, character_id: int | None = None) -> str:
        chart_rows = self.get_win_by_relic_number_points(character_id=character_id)
        if not chart_rows:
            return ""

        fig = px.line(
            chart_rows,
            x="total_relic",
            y="win_ratio",
            markers=True,
            title="Win Ratio by Total Relic Count",
        )
        fig.update_layout(
            xaxis_title="Nombre total de relics",
            yaxis_title="Ratio de victoire (%)",
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def get_win_by_relic_number_points(self, character_id: int | None = None) -> list[dict]:
        runs = RunSummary.objects.all()
        if character_id is not None:
            runs = runs.filter(character_id=character_id)

        run_rows = runs.annotate(total_relic=Count("relics", distinct=True)).values("win", "total_relic")

        if not run_rows:
            return []

        aggregated = {}
        for row in run_rows:
            relic_count = row["total_relic"]
            if relic_count not in aggregated:
                aggregated[relic_count] = {"run_count": 0, "win_count": 0}
            aggregated[relic_count]["run_count"] += 1
            if row["win"]:
                aggregated[relic_count]["win_count"] += 1

        chart_rows = []
        for relic_count, counters in sorted(aggregated.items(), key=lambda item: item[0]):
            run_count = counters["run_count"]
            win_count = counters["win_count"]
            win_ratio = round((win_count / run_count) * 100, 2) if run_count > 0 else 0.0
            chart_rows.append(
                {
                    "total_relic": relic_count,
                    "win_ratio": win_ratio,
                }
            )

        return chart_rows
