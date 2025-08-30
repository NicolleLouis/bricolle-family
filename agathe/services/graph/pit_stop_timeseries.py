import pandas as pd
import plotly.express as px

from agathe.constants.agathe import AgatheConstant
from agathe.models import PitStop


class PitStopTimeseriesChart:
    """Generate a line chart of pit stops per day."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE
        )
        records = [{"day": ps.start_date.date()} for ps in pit_stops]
        if not records:
            df = pd.DataFrame({"day": [], "count": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            df = (
                df.groupby("day")
                .size()
                .reindex(day_range, fill_value=0)
                .reset_index(name="count")
            )
            df = df.rename(columns={"index": "day"})
        fig = px.line(df, x="day", y="count")
        fig.update_layout(xaxis_title="Jour", yaxis_title="Nombre")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopDurationTimeseriesChart:
    """Generate a line chart of average pit stop duration per day."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            end_date__isnull=False,
        )
        records = [
            {"day": ps.start_date.date(), "duration": ps.duration} for ps in pit_stops
        ]
        if not records:
            df = pd.DataFrame({"day": [], "avg_duration": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            df = (
                df.groupby("day")["duration"]
                .mean()
                .reindex(day_range, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"index": "day", "duration": "avg_duration"})
        fig = px.line(df, x="day", y="avg_duration")
        fig.update_layout(xaxis_title="Jour", yaxis_title="Durée moyenne (Minutes)")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopIntervalTimeseriesChart:
    """Generate a line chart of average time between pit stops per day."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE
        ).order_by("start_date")
        records = []
        previous_end = None
        for ps in pit_stops:
            if previous_end:
                delta = ps.start_date - previous_end
                records.append(
                    {
                        "day": ps.start_date.date(),
                        "interval": delta.total_seconds() / (60 * 60),
                    }
                )
            if ps.end_date:
                previous_end = ps.end_date
        if not records:
            df = pd.DataFrame({"day": [], "avg_interval": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            df = (
                df.groupby("day")["interval"]
                .mean()
                .reindex(day_range, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"index": "day", "interval": "avg_interval"})
        fig = px.line(df, x="day", y="avg_interval")
        fig.update_layout(xaxis_title="Jour", yaxis_title="Interval moyen (Heures)")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopPerHourChart:
    """Generate a line chart of pit stops per hour."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE
        )
        records = [{"hour": ps.start_date.hour} for ps in pit_stops]
        hour_range = range(24)
        if not records:
            df = pd.DataFrame({"hour": list(hour_range), "count": [0] * 24})
        else:
            df = pd.DataFrame(records)
            df = (
                df.groupby("hour")
                .size()
                .reindex(hour_range, fill_value=0)
                .reset_index(name="count")
            )
        fig = px.line(df, x="hour", y="count")
        fig.update_layout(xaxis_title="Heure", yaxis_title="Nombre")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopDurationPerHourChart:
    """Generate a line chart of average pit stop duration per hour."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            end_date__isnull=False,
        )
        records = [
            {"hour": ps.start_date.hour, "duration": ps.duration}
            for ps in pit_stops
        ]
        hour_range = range(24)
        if not records:
            df = pd.DataFrame({"hour": list(hour_range), "avg_duration": [0] * 24})
        else:
            df = pd.DataFrame(records)
            df = (
                df.groupby("hour")["duration"]
                .mean()
                .reindex(hour_range, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"duration": "avg_duration"})
        fig = px.line(df, x="hour", y="avg_duration")
        fig.update_layout(
            xaxis_title="Heure", yaxis_title="Durée moyenne (Minutes)"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopIntervalPerHourChart:
    """Generate a line chart of average time between pit stops per hour."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE
        ).order_by("start_date")
        records = []
        previous_end = None
        for ps in pit_stops:
            if previous_end:
                delta = ps.start_date - previous_end
                records.append(
                    {
                        "hour": ps.start_date.hour,
                        "interval": delta.total_seconds() / (60 * 60),
                    }
                )
            if ps.end_date:
                previous_end = ps.end_date
        hour_range = range(24)
        if not records:
            df = pd.DataFrame({"hour": list(hour_range), "avg_interval": [0] * 24})
        else:
            df = pd.DataFrame(records)
            df = (
                df.groupby("hour")["interval"]
                .mean()
                .reindex(hour_range, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"interval": "avg_interval"})
        fig = px.line(df, x="hour", y="avg_interval")
        fig.update_layout(
            xaxis_title="Heure", yaxis_title="Interval moyen (Heures)"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
