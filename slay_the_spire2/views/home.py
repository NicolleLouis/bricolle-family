from django.shortcuts import render


def home(request):
    return render(request, "slay_the_spire2/home.html")
