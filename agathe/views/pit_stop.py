from django.shortcuts import render, redirect
from django.utils import timezone

from agathe.forms.pit_stop import PitStopForm
from agathe.models import PitStop
from agathe.services.graph.pit_stop_timeseries import (
    PitStopTimeseriesChart,
    PitStopQuantityTimeseriesChart,
    PitStopIntervalTimeseriesChart,
    PitStopPerHourChart,
    PitStopQuantityPerHourChart,
    PitStopIntervalPerHourChart,
    PitStopQuantityTotalTimeseriesChart,
)


class PitStopController:
    @staticmethod
    def pit_stop(request):
        if request.method == "POST":
            form = PitStopForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("agathe:pit_stop")
        else:
            now = timezone.now()
            form = PitStopForm(
                initial={
                    "start_date": now.strftime("%Y-%m-%dT%H:%M"),
                    "quantity": 90,
                }
            )
        pit_stops = PitStop.objects.all().order_by("-start_date")[:5]
        return render(
            request, "agathe/pit_stop.html", {"form": form, "pit_stops": pit_stops}
        )

    @staticmethod
    def stats(request):
        tab = request.GET.get("tab", "daily")
        context = {"tab": tab}
        if tab == "hour":
            context.update(
                {
                    "pit_stops_per_hour": PitStopPerHourChart.generate(),
                    "pit_stop_quantity_avg_per_hour": PitStopQuantityPerHourChart.generate(),
                    "pit_stop_interval_avg_per_hour": PitStopIntervalPerHourChart.generate(),
                }
            )
        else:
            context.update(
                {
                    "pit_stops_per_day": PitStopTimeseriesChart.generate(),
                    "pit_stop_quantity_avg_per_day": PitStopQuantityTimeseriesChart.generate(),
                    "pit_stop_interval_avg_per_day": PitStopIntervalTimeseriesChart.generate(),
                    "pit_stop_quantity_total_per_day": PitStopQuantityTotalTimeseriesChart.generate(),
                }
            )
        return render(request, "agathe/pit_stop_stats.html", context)
