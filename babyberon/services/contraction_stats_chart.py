from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate, ExtractHour
from django.utils import timezone
import plotly.express as px

from babyberon.models import Contraction


class ContractionStatsChartService:
    @staticmethod
    def generate_daily():
        """Return an HTML div containing the daily contraction bar chart."""
        today = timezone.now().date()
        since = today - timedelta(days=6)

        queryset = (
            Contraction.objects.filter(created_at__date__gte=since)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .order_by("day")
            .annotate(count=Count("id"))
        )
        counts_by_day = {item["day"]: item["count"] for item in queryset}

        dates = [since + timedelta(days=i) for i in range((today - since).days + 1)]
        labels = [d.strftime("%d/%m") for d in dates]
        counts = [counts_by_day.get(d, 0) for d in dates]

        fig = px.bar(x=labels, y=counts, labels={"x": "Jour", "y": "Contractions"})
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

        return fig.to_html(full_html=False, include_plotlyjs='cdn')

    @staticmethod
    def generate_hourly():
        """Return an HTML div containing the hourly contraction line chart."""
        queryset = (
            Contraction.objects.annotate(hour=ExtractHour("created_at"))
            .values("hour")
            .order_by("hour")
            .annotate(count=Count("id"))
        )
        counts_by_hour = {item["hour"]: item["count"] for item in queryset}

        hours = list(range(24))
        labels = [f"{h:02d}h" for h in hours]
        counts = [counts_by_hour.get(h, 0) for h in hours]

        fig = px.line(x=labels, y=counts, labels={"x": "Heure", "y": "Contractions"})
        fig.update_layout(margin=dict(l=20, r=20, t=20, b=20))

        return fig.to_html(full_html=False, include_plotlyjs='cdn')
