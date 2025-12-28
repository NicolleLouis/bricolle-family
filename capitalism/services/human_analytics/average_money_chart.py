from __future__ import annotations

from typing import List

import plotly.express as px
from django.apps import apps


class AverageMoneyChartService:
    """Render a line chart of average money per day for a job."""

    LINE_COLOR = "#0d6efd"  # Bootstrap primary blue

    def render(self, *, job: str) -> str:
        human_analytics_model = apps.get_model("capitalism", "HumanAnalytics")
        analytics = (
            human_analytics_model.objects.filter(job=job)
            .order_by("day_number")
            .values_list("day_number", "average_money")
        )
        if not analytics:
            return ""

        days: List[int] = [day for day, _ in analytics]
        averages: List[float] = [value or 0.0 for _, value in analytics]

        fig = px.line(
            x=days,
            y=averages,
            labels={"x": "Day", "y": "Average Money"},
            title="Average Money Over Time",
        )
        fig.update_traces(line_color=self.LINE_COLOR)
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

        return fig.to_html(full_html=False, include_plotlyjs="cdn")
