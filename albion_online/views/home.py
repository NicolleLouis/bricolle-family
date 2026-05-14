from django.shortcuts import render


def home(request):
    return render(request, "albion_online/home.html")
