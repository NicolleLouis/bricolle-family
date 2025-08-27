from django.shortcuts import redirect
from django.utils import timezone

from agathe.models import VitaminIntake


class VitaminIntakeController:
    @staticmethod
    def create(request):
        if request.method == "POST":
            VitaminIntake.objects.create(date=timezone.now())
        return redirect("agathe:home")
