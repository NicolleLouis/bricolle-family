from django.shortcuts import render

class SummaryView:
    @staticmethod
    def home(request):
        modules = [
            {"name": "Agathe", "url": "/agathe/", "color": "#e09cff"},
            {"name": "Shopping List", "url": "/shopping_list/", "color": "#58d68d"},
            {"name": "Games", "url": "/games", "color": "#ffbe5c"},
            {"name": "More...", "url": "/more", "color": "#3498db"},
        ]
        return render(request, "bricolle_family/summary.html", {"modules": modules})

    @staticmethod
    def games(request):
        modules = [
            {"name": "Altered", "url": "/altered/", "color": "#2C3E50"},
            {"name": "Runeterra", "url": "/runeterra/", "color": "#4A7F4C"},
            {"name": "Games Collection", "url": "/games_collection/", "color": "#8e44ad"},
            {"name": "The Bazaar", "url": "/the_bazaar/", "color": "#5DADE2"},
        ]
        return render(request, "bricolle_family/summary.html", {"modules": modules})

    @staticmethod
    def more(request):
        modules = [
            {"name": "Admin", "url": "/admin/", "color": "#3498db"},
            {"name": "Baby Name", "url": "/baby_name/", "color": "#ff6b6b"},
            {"name": "Battery Simulator", "url": "/battery_simulator/", "color": "#ffbe5c"},
            {"name": "Documents", "url": "/documnents/", "color": "#4A7F4C"},
        ]
        return render(request, "bricolle_family/summary.html", {"modules": modules})
