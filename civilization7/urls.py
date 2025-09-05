from django.urls import path

from civilization7 import views

app_name = "civilization7"

urlpatterns = [
    path("", views.recent_games, name="recent_games"),
    path("stats/", views.stats, name="stats"),
    path("bingo/leader/", views.bingo_leader, name="bingo_leader"),
    path("bingo/civilization/", views.bingo_civilization, name="bingo_civilization"),
    path("game/create/", views.game_create, name="game_create"),
    path("game/<int:pk>/update/", views.game_update, name="game_update"),
]
