from django.shortcuts import render


def home(request):
    modules = [
        {"name": "Admin", "url": "/admin/", "color": "#39d358"},
        {"name": "Baby Name", "url": "/baby_name/", "color": "#e86763"},
        {"name": "Babyberon", "url": "/babyberon/", "color": "#e6b3ff"},
        {"name": "The Bazaar", "url": "/the_bazaar/", "color": "#ffc34d"},
        {"name": "Shopping List", "url": "/shopping_list/", "color": "#259ad8"},
    ]
    return render(request, "bricolle_family/home.html", {"modules": modules})
