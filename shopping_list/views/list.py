from django.shortcuts import render


def shopping_list(request):
    return render(request, "shopping_list/error.html", {"message": "Not Implemented"})
