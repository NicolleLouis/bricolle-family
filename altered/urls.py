from django.urls import path

from altered.views import game_form_view
from altered.views.deck_stats import deck_stats_view
from altered.views.meta_stats import meta_stats_view
from altered.views.career import career_view
from altered.views.unique_flip import (
    unique_flip_list_view,
    unique_flip_detail_view,
)

app_name = "altered"

urlpatterns = [
    path("", game_form_view, name="home"),
    path('game/', game_form_view, name='game_form'),
    path('decks/', deck_stats_view, name='deck_stats'),
    path('meta/', meta_stats_view, name='meta_stats'),
    path('career/', career_view, name='career'),
    path('flips/', unique_flip_list_view, name='unique_flip_list'),
    path('flips/<int:flip_id>/', unique_flip_detail_view, name='unique_flip_detail'),
]
