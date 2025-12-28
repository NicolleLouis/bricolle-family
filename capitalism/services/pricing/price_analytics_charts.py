from __future__ import annotations

from typing import List, Tuple

import plotly.express as px
from django.apps import apps


class PriceAnalyticsChartsService:
    """Render line charts for average accepted price and transaction count."""

    AVERAGE_COLOR = "#0d6efd"  # Bootstrap primary blue
    TRANSACTION_COLOR = "#198754"  # Bootstrap success green

    def render(self, *, object_type: str) -> Tuple[str, str]:
        price_analytics_model = apps.get_model("capitalism", "PriceAnalytics")
        analytics = (
            price_analytics_model.objects.filter(object_type=object_type)
            .order_by("day_number")
            .values_list("day_number", "average_price", "transaction_number")
        )
        if not analytics:
            return "", ""

        days: List[int] = [day for day, _avg, _count in analytics]
        averages: List[float] = [avg or 0.0 for _day, avg, _count in analytics]
        transactions: List[int] = [count or 0 for _day, _avg, count in analytics]

        average_fig = px.line(
            x=days,
            y=averages,
            labels={"x": "Day", "y": "Average Accepted Price"},
            title="Average Accepted Price",
        )
        average_fig.update_traces(line_color=self.AVERAGE_COLOR)
        average_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

        transaction_fig = px.line(
            x=days,
            y=transactions,
            labels={"x": "Day", "y": "Transactions"},
            title="Transactions per Day",
        )
        transaction_fig.update_traces(line_color=self.TRANSACTION_COLOR)
        transaction_fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))

        average_chart = average_fig.to_html(full_html=False, include_plotlyjs="cdn")
        transaction_chart = transaction_fig.to_html(full_html=False, include_plotlyjs=False)

        return average_chart, transaction_chart
