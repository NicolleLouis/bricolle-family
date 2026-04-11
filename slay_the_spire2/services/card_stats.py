from django.db.models import Count, Q, Sum
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from slay_the_spire2.models.card import Card
from slay_the_spire2.models.run_summary import RunSummary


class CardStatsService:
    _DEFAULT_SORT_BY = "win_number"
    _DEFAULT_DIRECTION = "desc"
    _ALLOWED_SORT_FIELDS = {
        "card_name",
        "run_number",
        "win_number",
        "win_percentage",
    }

    def get_card_stats(
        self,
        sort_by: str | None = None,
        direction: str | None = None,
        character_id: int | None = None,
    ) -> list[dict]:
        character_filter = Q()
        if character_id is not None:
            character_filter = Q(run_summaries__character_id=character_id)

        rows = Card.objects.annotate(
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
                    "card_name": row.name,
                    "run_number": run_number,
                    "win_number": win_number,
                    "win_percentage": win_percentage,
                }
            )

        normalized_sort_by = sort_by if sort_by in self._ALLOWED_SORT_FIELDS else self._DEFAULT_SORT_BY
        normalized_direction = direction if direction in {"asc", "desc"} else self._DEFAULT_DIRECTION
        reverse = normalized_direction == "desc"

        if normalized_sort_by == "card_name":
            return sorted(stats, key=lambda stat: stat["card_name"].lower(), reverse=reverse)
        return sorted(stats, key=lambda stat: stat[normalized_sort_by], reverse=reverse)

    def get_win_by_card_number_chart(self, character_id: int | None = None) -> str:
        chart_rows = self.get_win_by_card_number_points(character_id=character_id)
        if not chart_rows:
            return ""

        fig = px.line(
            chart_rows,
            x="total_card",
            y="win_ratio",
            markers=True,
            title="Win Ratio by Total Card Count",
        )
        fig.update_layout(
            xaxis_title="Nombre total de cartes",
            yaxis_title="Ratio de victoire (%)",
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def get_win_by_card_number_points(self, character_id: int | None = None) -> list[dict]:
        runs = RunSummary.objects.all()
        if character_id is not None:
            runs = runs.filter(character_id=character_id)

        run_rows = runs.annotate(total_card=Sum("deck_entries__quantity")).values("win", "total_card")

        if not run_rows:
            return []

        aggregated = {}
        for row in run_rows:
            card_count = row["total_card"] or 0
            if card_count not in aggregated:
                aggregated[card_count] = {"run_count": 0, "win_count": 0}
            aggregated[card_count]["run_count"] += 1
            if row["win"]:
                aggregated[card_count]["win_count"] += 1

        chart_rows = []
        for card_count, counters in sorted(aggregated.items(), key=lambda item: item[0]):
            run_count = counters["run_count"]
            win_count = counters["win_count"]
            win_ratio = round((win_count / run_count) * 100, 2) if run_count > 0 else 0.0
            chart_rows.append(
                {
                    "total_card": card_count,
                    "win_ratio": win_ratio,
                }
            )

        return chart_rows

    def get_win_by_basic_card_count_chart(self, character_id: int | None = None) -> str:
        return self._build_basic_card_combined_chart(
            target_card_names=["Strike", "Defend"],
            title="Win Ratio and Run Count by Strike + Defend Count",
            xaxis_title="Nombre total de Strike + Defend",
            character_id=character_id,
        )

    def get_win_by_strike_count_chart(self, character_id: int | None = None) -> str:
        return self._build_basic_card_combined_chart(
            target_card_names=["Strike"],
            title="Win Ratio and Run Count by Strike Count",
            xaxis_title="Nombre total de Strike",
            character_id=character_id,
        )

    def get_win_by_defend_count_chart(self, character_id: int | None = None) -> str:
        return self._build_basic_card_combined_chart(
            target_card_names=["Defend"],
            title="Win Ratio and Run Count by Defend Count",
            xaxis_title="Nombre total de Defend",
            character_id=character_id,
        )

    def _build_basic_card_combined_chart(
        self,
        target_card_names: list[str],
        title: str,
        xaxis_title: str,
        character_id: int | None = None,
    ) -> str:
        chart_rows = self._get_win_by_specific_card_count_points(
            target_card_names=target_card_names,
            character_id=character_id,
        )
        if not chart_rows:
            return ""

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=[row["card_count"] for row in chart_rows],
                y=[row["run_count"] for row in chart_rows],
                name="Run Count",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=[row["card_count"] for row in chart_rows],
                y=[row["win_ratio"] for row in chart_rows],
                name="Win Ratio",
                mode="lines+markers",
            ),
            secondary_y=True,
        )
        fig.update_layout(
            title=title,
            xaxis_title=xaxis_title,
            legend_title_text="Metric",
            bargap=0.6,
        )
        fig.update_yaxes(title_text="Nombre de parties", secondary_y=False)
        fig.update_yaxes(title_text="Ratio de victoire (%)", secondary_y=True)
        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def _get_win_by_specific_card_count_points(
        self,
        target_card_names: list[str],
        character_id: int | None = None,
    ) -> list[dict]:
        runs = RunSummary.objects.all()
        if character_id is not None:
            runs = runs.filter(character_id=character_id)

        run_rows = runs.annotate(
            card_count=Sum(
                "deck_entries__quantity",
                filter=Q(deck_entries__card__name__in=target_card_names),
            )
        ).values("win", "card_count")

        if not run_rows:
            return []

        aggregated = {}
        for row in run_rows:
            card_count = row["card_count"] or 0
            if card_count not in aggregated:
                aggregated[card_count] = {"run_count": 0, "win_count": 0}
            aggregated[card_count]["run_count"] += 1
            if row["win"]:
                aggregated[card_count]["win_count"] += 1

        chart_rows = []
        for card_count, counters in sorted(aggregated.items(), key=lambda item: item[0]):
            run_count = counters["run_count"]
            win_count = counters["win_count"]
            win_ratio = round((win_count / run_count) * 100, 2) if run_count > 0 else 0.0
            chart_rows.append(
                {
                    "card_count": card_count,
                    "win_ratio": win_ratio,
                    "run_count": run_count,
                }
            )

        return chart_rows
