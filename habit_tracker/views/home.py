from django.shortcuts import render


def home(request):
    return render(request, "habit_tracker/home.html")
