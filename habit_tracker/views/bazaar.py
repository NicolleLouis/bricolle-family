from django.shortcuts import render


def bazaar(request):
    return render(request, "habit_tracker/bazaar.html")
