from django.shortcuts import render, redirect
from django.utils import timezone

from agathe.forms.diaper_change import DiaperChangeForm
from agathe.models import DiaperChange


class DiaperChangeController:
    @staticmethod
    def diaper_change(request):
        if request.method == "POST":
            form = DiaperChangeForm(request.POST)
            if form.is_valid():
                DiaperChange.objects.create(date=timezone.now())
                return redirect("agathe:diaper_change")
        else:
            form = DiaperChangeForm()
        changes = DiaperChange.objects.all().order_by("-date")[:5]
        return render(request, "agathe/diaper_change.html", {"form": form, "changes": changes})

    @staticmethod
    def quick(request):
        if request.method == "POST":
            DiaperChange.objects.create(date=timezone.now())
        return redirect("agathe:home")
