from django.shortcuts import render

def meal(request):
    return render(request, "shopping_list/error.html", {"message": "Not Implemented"})
