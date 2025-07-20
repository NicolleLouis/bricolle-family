from django.shortcuts import render


def home(request):
    return render(request, "battery_simulator/home.html")
