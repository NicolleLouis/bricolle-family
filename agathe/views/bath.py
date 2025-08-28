from django.shortcuts import redirect
from django.utils import timezone

from agathe.models import Bath


class BathController:
    @staticmethod
    def create(request):
        if request.method == "POST":
            Bath.objects.create(date=timezone.now())
        return redirect("agathe:home")
