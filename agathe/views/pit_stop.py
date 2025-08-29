from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from agathe.forms.pit_stop import PitStopForm
from agathe.models import PitStop


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
        return render(request, "agathe/pit_stop.html", {"form": form, "pit_stops": pit_stops})

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
