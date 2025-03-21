from django.urls import path

from .views.index import index
from .views.interface import interface
from .views.leaderboard import leaderboard
from .views.login import register, user_login, user_logout
from .views.ranking import ranking
from .views.ranking_vote import ranking_vote
from .views.results import results
from .views.vote import vote

app_name = "baby_name"

urlpatterns = [
    path("", index, name="index"),
    path("interface/", interface, name="interface"),
    path("vote/", vote, name="vote"),
    path("results/", results, name="results"),
    path("ranking/", ranking, name="ranking"),
    path("ranking_vote/", ranking_vote, name="ranking_vote"),
    path("leaderboard/", leaderboard, name="leaderboard"),
    path("register/", register, name="register"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
]
