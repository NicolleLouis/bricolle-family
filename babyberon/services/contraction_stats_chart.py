from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
import plotly.express as px
import plotly.offline as opy

from babyberon.models import Contraction


class ContractionStatsChartService:
    @staticmethod
    def generate():
        """Return an HTML div containing the contraction stats bar chart."""
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

        return opy.plot(fig, auto_open=False, output_type="div")
