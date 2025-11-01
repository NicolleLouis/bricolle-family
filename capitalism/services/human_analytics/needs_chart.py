from __future__ import annotations

from typing import Dict, List

import plotly.express as px
from django.apps import apps


class HumanNeedsSatisfactionChartService:
    """Render a donut chart summarising recent basic-need fulfilment."""

    COLORS: Dict[str, str] = {
        "Needs Met": "#198754",  # Bootstrap success green
        "Needs Unmet": "#dc3545",  # Bootstrap danger red
    }

    def render(self) -> str:
        counts = self._counts()
        if not counts:
            return ""

        labels: List[str] = list(counts.keys())
        values: List[int] = [counts[label] for label in labels]

        fig = px.pie(
            names=labels,
            values=values,
            hole=0.5,
            title="Basic Need Fulfilment",
            color=labels,
            color_discrete_map=self.COLORS,
        )
        fig.update_traces(textinfo="percent+label")

        return fig.to_html(full_html=False, include_plotlyjs="cdn")

    def _counts(self) -> Dict[str, int]:
        Human = self._human_model()
        eligible = Human.objects.filter(age__gt=0)
        satisfied = eligible.filter(time_since_need_fulfilled=0).count()
        unsatisfied = eligible.filter(time_since_need_fulfilled__gt=0).count()

        counts: Dict[str, int] = {}
        if satisfied > 0:
            counts["Needs Met"] = satisfied
        if unsatisfied > 0:
            counts["Needs Unmet"] = unsatisfied
        return counts

    @staticmethod
    def _human_model():
        return apps.get_model("capitalism", "Human")
