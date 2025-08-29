import pandas as pd
import plotly.express as px
from datetime import date

from agathe.models import PitStop


class PitStopTimeseriesService:
    """Generate a line chart of pit stops per day."""

    START_DATE = date(2024, 8, 28)

    @classmethod
    def generate(cls):
        pit_stops = PitStop.objects.filter(start_date__date__gte=cls.START_DATE)
        records = [{"day": ps.start_date.date()} for ps in pit_stops]
        if not records:
            df = pd.DataFrame({"day": [], "count": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(start=cls.START_DATE, end=df["day"].max())
            df = (
                df.groupby("day")
                .size()
                .reindex(day_range, fill_value=0)
                .reset_index(name="count")
            )
        fig = px.line(df, x="day", y="count")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
