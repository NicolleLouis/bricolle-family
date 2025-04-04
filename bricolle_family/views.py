from django.shortcuts import render


def home(request):
    modules = [
        {"name": "Shopping List", "url": "/shopping_list/", "color": "#259ad8"},
        {"name": "Baby Name", "url": "/baby_name/", "color": "#e86763"},
        {"name": "Admin", "url": "/admin/", "color": "#39d358"},
    ]
    return render(request, "bricolle_family/home.html", {"modules": modules})
