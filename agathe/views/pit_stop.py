from django.shortcuts import render, redirect

from agathe.forms.pit_stop import PitStopForm
from agathe.models import PitStop


class PitStopController:
    @staticmethod
    def pit_stop(request):
        if request.method == "POST":
            form = PitStopForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("agathe:pit_stop")
        else:
            form = PitStopForm()
        pit_stops = PitStop.objects.all().order_by("-start_date")[:5]
        return render(request, "agathe/pit_stop.html", {"form": form, "pit_stops": pit_stops})
