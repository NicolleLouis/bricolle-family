from django.urls import path

from baby_name.views.epuration import user_epuration
from .views.evaluation_delete import evaluation_delete

from .views.global_leaderboard import global_leaderboard
from .views.home import home
from .views.user_leaderboard import user_leaderboard
from .views.login import Login
from .views.ranking import Ranking
from .views.results import results
from .views.vote import Vote

app_name = "baby_name"

urlpatterns = [
    path("", home, name="home"),
    path("epuration/", user_epuration, name="epuration"),
    path("evaluation_delete/", evaluation_delete, name="evaluation_delete"),
    path("global_leaderboard/", global_leaderboard, name="global_leaderboard"),
    path("login/", Login.user_login, name="login"),
    path("logout/", Login.user_logout, name="logout"),
    path("ranking/", Ranking.form, name="ranking"),
    path("ranking_vote/", Ranking.post, name="ranking_vote"),
    path("register/", Login.register, name="register"),
    path("results/", results, name="results"),
    path("user_leaderboard/", user_leaderboard, name="user_leaderboard"),
    path("vote/", Vote.post, name="vote"),
    path("vote_form/", Vote.form, name="vote_form"),
]
