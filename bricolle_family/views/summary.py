from django.shortcuts import render

class SummaryView:
    @staticmethod
    def home(request):
        modules = [
            {"name": "Agathe", "url": "/agathe/", "color": "#e09cff"},
            {"name": "Flash Cards", "url": "/flash_cards/", "color": "#16a085"},
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
            {"name": "Civilization 7", "url": "/civilization7/", "color": "#d35400"},
        ]
        return render(request, "bricolle_family/summary.html", {"modules": modules})

    @staticmethod
    def more(request):
        modules = [
            {"name": "Admin", "url": "/admin/", "color": "#3498db"},
            {"name": "Baby Name", "url": "/baby_name/", "color": "#ff6b6b"},
            {"name": "Finance Simulator", "url": "/finance_simulator/", "color": "#1abc9c"},
            {"name": "Documents", "url": "/documents/", "color": "#4A7F4C"},
            {"name": "Capitalism", "url": "/capitalism/", "color": "#2ecc71"},
            {"name": "Chess", "url": "/chess/", "color": "#7f8c8d"},
        ]
        return render(request, "bricolle_family/summary.html", {"modules": modules})
