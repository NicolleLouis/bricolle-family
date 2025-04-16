from django.shortcuts import render


def home(request):
    return render(request, "baby_name/home.html")
