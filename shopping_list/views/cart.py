from django.shortcuts import render


def cart(request):
    return render(request, "shopping_list/error.html", {"message": "Not Implemented"})
