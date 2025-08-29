from django.shortcuts import redirect
from django.utils import timezone

from agathe.models import AspirinIntake


class AspirinIntakeController:
    @staticmethod
    def create(request):
        if request.method == "POST":
            AspirinIntake.objects.create(date=timezone.now())
        return redirect("agathe:home")
