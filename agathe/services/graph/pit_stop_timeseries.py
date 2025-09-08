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
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            delay_before_next_pit_stop__isnull=False,
        )
        records = [
            {
                "day": ps.start_date.date(),
                "interval": ps.delay_before_next_pit_stop / 60,
            }
            for ps in pit_stops
        ]
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
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            delay_before_next_pit_stop__isnull=False,
        )
        records = [
            {
                "hour": ps.start_date.hour,
                "interval": ps.delay_before_next_pit_stop / 60,
            }
            for ps in pit_stops
        ]
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
            df = df.rename(columns={"index": "hour", "interval": "avg_interval"})
        fig = px.line(df, x="hour", y="avg_interval")
        fig.update_layout(
            xaxis_title="Heure", yaxis_title="Interval moyen (Heures)"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopDurationTotalTimeseriesChart:
    """Generate a line chart of total pit stop duration per day."""

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
            df = pd.DataFrame({"day": [], "total_duration": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            df = (
                df.groupby("day")["duration"]
                .sum()
                .reindex(day_range, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"index": "day", "duration": "total_duration"})
        fig = px.line(df, x="day", y="total_duration")
        fig.update_layout(xaxis_title="Jour", yaxis_title="Durée totale (Minutes)")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopPerDayBySideChart:
    """Generate a line chart of pit stop count per day and side."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE
        )
        records = [
            {"day": ps.start_date.date(), "side": ps.get_side_display()}
            for ps in pit_stops
        ]
        side_labels = [choice.label for choice in PitStop.Side]
        if not records:
            df = pd.DataFrame({"day": [], "side": [], "count": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            index = pd.MultiIndex.from_product(
                [day_range, side_labels], names=["day", "side"]
            )
            df = (
                df.groupby(["day", "side"])
                .size()
                .reindex(index, fill_value=0)
                .reset_index(name="count")
            )
        fig = px.line(df, x="day", y="count", color="side")
        fig.update_layout(xaxis_title="Jour", yaxis_title="Nombre")
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopDurationAvgPerDayBySideChart:
    """Generate a line chart of average pit stop duration per day and side."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            end_date__isnull=False,
        )
        records = [
            {
                "day": ps.start_date.date(),
                "side": ps.get_side_display(),
                "duration": ps.duration,
            }
            for ps in pit_stops
        ]
        side_labels = [choice.label for choice in PitStop.Side]
        if not records:
            df = pd.DataFrame({"day": [], "side": [], "avg_duration": []})
        else:
            df = pd.DataFrame(records)
            day_range = pd.date_range(
                start=AgatheConstant.GRAPH_START_DATE, end=df["day"].max()
            )
            index = pd.MultiIndex.from_product(
                [day_range, side_labels], names=["day", "side"]
            )
            df = (
                df.groupby(["day", "side"])["duration"]
                .mean()
                .reindex(index, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"duration": "avg_duration"})
        fig = px.line(df, x="day", y="avg_duration", color="side")
        fig.update_layout(
            xaxis_title="Jour", yaxis_title="Durée moyenne (Minutes)"
        )
        return fig.to_html(full_html=False, include_plotlyjs="cdn")


class PitStopDurationTotalBySideChart:
    """Generate a donut chart of total pit stop duration by side."""

    @staticmethod
    def generate():
        pit_stops = PitStop.objects.filter(
            start_date__date__gte=AgatheConstant.GRAPH_START_DATE,
            end_date__isnull=False,
        )
        records = [
            {"side": ps.get_side_display(), "duration": ps.duration} for ps in pit_stops
        ]
        side_labels = [choice.label for choice in PitStop.Side]
        if not records:
            df = pd.DataFrame({"side": side_labels, "total_duration": [0] * len(side_labels)})
        else:
            df = pd.DataFrame(records)
            df = (
                df.groupby("side")["duration"]
                .sum()
                .reindex(side_labels, fill_value=0)
                .reset_index()
            )
            df = df.rename(columns={"duration": "total_duration"})
        fig = px.pie(df, values="total_duration", names="side", hole=0.4)
        fig.update_layout(showlegend=True)
        return fig.to_html(full_html=False, include_plotlyjs="cdn")
