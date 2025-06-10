from django.urls import path

from altered.views.home import home
from altered.views import game_form_view
from altered.views.deck_stats import deck_stats_view
from altered.views.meta_stats import meta_stats_view

app_name = "altered"

urlpatterns = [
    path("", home, name="home"),
    path('game/', game_form_view, name='game_form'),
    path('decks/', deck_stats_view, name='deck_stats'),
    path('meta/', meta_stats_view, name='meta_stats'),
]
