from django.shortcuts import render

from runeterra.models import Champion


def random_picker(request):
    champion = None
    if request.method == "POST":
        champion = Champion.objects.order_by("?").first()
    return render(request, "runeterra/random_picker.html", {"champion": champion})
