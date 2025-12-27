from django.shortcuts import render


def home(request):
    return render(request, "seven_and_half/home.html")
