from django.shortcuts import render

from baby_name.models import Name


def home(request):
    return render(request, "baby_name/home.html")
