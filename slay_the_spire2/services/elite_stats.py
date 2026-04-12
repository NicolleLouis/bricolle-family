from django.db.models import Avg, Count, Q
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from slay_the_spire2.models.encounter import Encounter
from slay_the_spire2.models.run_encounter import RunEncounter
from slay_the_spire2.models.run_summary import RunSummary


class EliteStatsService:
    def get_elite_dangerousness_stats(
        self,
        character_id: int | None = None,
        act: int | None = None,
    ) -> list[dict]:
        encounter_rows = RunEncounter.objects.filter(
            encounter__type=Encounter.Type.ELITE,
        )
        if character_id is not None:
            encounter_rows = encounter_rows.filter(run_summary__character_id=character_id)
        if act is not None:
            encounter_rows = encounter_rows.filter(act=act)

        rows = (
            encounter_rows.values("encounter__name")
            .annotate(
                average_damage_taken=Avg("damage_taken"),
            )
            .order_by("-average_damage_taken", "encounter__name")
        )

        return [
            {
                "encounter_name": row["encounter__name"],
                "average_damage_taken": round(row["average_damage_taken"] or 0.0, 2),
            }
            for row in rows
        ]

    def get_win_rate_by_elite_count_chart(
        self,
        character_id: int | None = None,
        act: int | None = None,
    ) -> str:
        chart_rows = self._get_win_rate_by_elite_count_points(character_id=character_id, act=act)
        if not chart_rows:
            return ""

        if act is None:
            title = "Win Ratio and Run Count by Elite Encountered Count"
        else:
            title = f"Act {act + 1} - Win Ratio and Run Count by Elite Encountered Count"

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=[row["elite_count"] for row in chart_rows],
                y=[row["run_count"] for row in chart_rows],
                name="Run Count",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=[row["elite_count"] for row in chart_rows],
                y=[row["win_ratio"] for row in chart_rows],
                name="Win Ratio",
                mode="lines+markers",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title=title,
            xaxis_title="Nombre d'Elite rencontres",
            legend_title_text="Metric",
            bargap=0.6,
        )
        fig.update_yaxes(title_text="Nombre de parties", secondary_y=False)
        fig.update_yaxes(title_text="Ratio de victoire (%)", secondary_y=True)
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def _get_win_rate_by_elite_count_points(
        self,
        character_id: int | None = None,
        act: int | None = None,
    ) -> list[dict]:
        runs = RunSummary.objects.all()
        if character_id is not None:
            runs = runs.filter(character_id=character_id)

        encounter_filter = Q(encounters__encounter__type=Encounter.Type.ELITE)
        if act is not None:
            encounter_filter &= Q(encounters__act=act)

        run_rows = runs.annotate(
            elite_count=Count("encounters", filter=encounter_filter),
        ).values("win", "elite_count")

        if not run_rows:
            return []

        aggregated = {}
        for row in run_rows:
            elite_count = row["elite_count"] or 0
            if elite_count not in aggregated:
                aggregated[elite_count] = {"run_count": 0, "win_count": 0}
            aggregated[elite_count]["run_count"] += 1
            if row["win"]:
                aggregated[elite_count]["win_count"] += 1

        chart_rows = []
        for elite_count, counters in sorted(aggregated.items(), key=lambda item: item[0]):
            run_count = counters["run_count"]
            win_count = counters["win_count"]
            win_ratio = round((win_count / run_count) * 100, 2) if run_count > 0 else 0.0
            chart_rows.append(
                {
                    "elite_count": elite_count,
                    "win_ratio": win_ratio,
                    "run_count": run_count,
                }
            )

        return chart_rows
