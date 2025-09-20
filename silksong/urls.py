from django.urls import path

from silksong.views import (
    boss_fight_sessions,
    home,
    ideas,
    objectives,
    speedrun_sessions,
    steel_soul_sessions,
)

app_name = "silksong"

urlpatterns = [
    path("", home, name="home"),
    path("objectives/", objectives, name="objectives"),
    path("ideas/", ideas, name="ideas"),
    path("speedrun/", speedrun_sessions, name="speedrun_sessions"),
    path("steel-soul/", steel_soul_sessions, name="steel_soul_sessions"),
    path("boss-fight/", boss_fight_sessions, name="boss_fight_sessions"),
]
