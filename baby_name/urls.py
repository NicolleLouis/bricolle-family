from django.urls import path

from baby_name.views.epuration import user_epuration
from .views.add_name import add_name
from .views.evaluation import EvaluationController

from .views.global_leaderboard import global_leaderboard
from .views.home import home
from .views.user_leaderboard import user_leaderboard
from .views.ranking import Ranking
from .views.results import results
from .views.vote import Vote

app_name = "baby_name"

urlpatterns = [
    path("", home, name="home"),
    path("epuration/", user_epuration, name="epuration"),
    path("evaluation/delete", EvaluationController.delete, name="evaluation_delete"),
    path("evaluation/update", EvaluationController.get_or_update, name="evaluation_update"),
    path("global_leaderboard/", global_leaderboard, name="global_leaderboard"),
    path("name/new", add_name, name="add_name"),
    path("ranking/", Ranking.form, name="ranking"),
    path("ranking_vote/", Ranking.post, name="ranking_vote"),
    path("results/", results, name="results"),
    path("user_leaderboard/", user_leaderboard, name="user_leaderboard"),
    path("vote/", Vote.post, name="vote"),
    path("vote_form/", Vote.form, name="vote_form"),
]
