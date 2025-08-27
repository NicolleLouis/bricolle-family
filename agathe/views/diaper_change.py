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
                change = form.save(commit=False)
                change.date = timezone.now()
                change.save()
                return redirect("agathe:diaper_change")
        else:
            form = DiaperChangeForm()
        changes = DiaperChange.objects.all().order_by("-date")[:5]
        return render(request, "agathe/diaper_change.html", {"form": form, "changes": changes})
