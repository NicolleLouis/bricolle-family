from django.shortcuts import render


def home(request):
    modules = [
        {"name": "Admin", "url": "/admin/", "color": "#3498db"},
        {"name": "Altered", "url": "/altered/", "color": "#2C3E50"},
        {"name": "Baby Name", "url": "/baby_name/", "color": "#ff6b6b"},
        {"name": "Babyberon", "url": "/babyberon/", "color": "#e09cff"},
        {"name": "Northguard", "url": "/northguard/", "color": "#ffbe5c"},
        {"name": "Shopping List", "url": "/shopping_list/", "color": "#58d68d"},
        {"name": "The Bazaar", "url": "/the_bazaar/", "color": "#5DADE2"},
    ]
    return render(request, "bricolle_family/home.html", {"modules": modules})
