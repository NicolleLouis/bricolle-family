from django.shortcuts import render


def home(request):
    return render(request, "shopping_list/home.html")
