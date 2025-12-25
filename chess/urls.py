from django.urls import path

from chess.views.home import home
from chess.views.openings import openings_config

app_name = "chess"

urlpatterns = [
    path("", home, name="home"),
    path("openings/", openings_config, name="openings"),
]
