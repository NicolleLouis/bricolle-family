from django.urls import path

from .views.index import index
from .views.leaderboard import leaderboard
from .views.login import Login
from .views.ranking import Ranking
from .views.results import results
from .views.vote import Vote

app_name = "baby_name"

urlpatterns = [
    path("", index, name="index"),
    path("interface/", Vote.form, name="interface"),
    path("vote/", Vote.post, name="vote"),
    path("results/", results, name="results"),
    path("ranking/", Ranking.form, name="ranking"),
    path("ranking_vote/", Ranking.post, name="ranking_vote"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("register/", Login.register, name="register"),
    path("login/", Login.user_login, name="login"),
    path("logout/", Login.user_logout, name="logout"),
]
