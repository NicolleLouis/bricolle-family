from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from agathe.forms.pit_stop import PitStopForm
from agathe.models import PitStop
from agathe.services.graph.pit_stop_timeseries import PitStopTimeseriesChart


class PitStopController:
    @staticmethod
    def pit_stop(request):
        if request.method == "POST":
            form = PitStopForm(request.POST)
            if form.is_valid():
                pit_stop = form.save(commit=False)
                pit_stop.start_date = timezone.now()
                pit_stop.save()
                return redirect("agathe:pit_stop")
        else:
            form = PitStopForm()
        pit_stops = PitStop.objects.all().order_by("-start_date")[:5]
        return render(
            request, "agathe/pit_stop.html", {"form": form, "pit_stops": pit_stops}
        )

    @staticmethod
    def finish(request, pk):
        if request.method == "POST":
            pit_stop = get_object_or_404(PitStop, pk=pk, end_date__isnull=True)
            pit_stop.end_date = timezone.now()
            pit_stop.save()
        return redirect("agathe:pit_stop")

    @staticmethod
    def finish_current(request):
        if request.method == "POST":
            pit_stop = (
                PitStop.objects.filter(end_date__isnull=True)
                .order_by("-start_date")
                .first()
            )
            if pit_stop:
                pit_stop.end_date = timezone.now()
                pit_stop.save()
        return redirect("agathe:home")

    @staticmethod
    def stats(request):
        pit_stops_per_day = PitStopTimeseriesChart.generate()
        return render(
            request,
            "agathe/pit_stop_stats.html",
            {"pit_stops_per_day": pit_stops_per_day},
        )

    @staticmethod
    def start(request):
        if request.method == "POST":
            last = PitStop.objects.order_by("-start_date").first()
            if last and last.side == PitStop.Side.LEFT:
                side = PitStop.Side.RIGHT
            else:
                side = PitStop.Side.LEFT
            PitStop.objects.create(start_date=timezone.now(), side=side)
        return redirect("agathe:home")
