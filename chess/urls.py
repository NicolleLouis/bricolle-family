from django.urls import path

from chess.views.home import home

app_name = "chess"

urlpatterns = [
    path("", home, name="home"),
]
