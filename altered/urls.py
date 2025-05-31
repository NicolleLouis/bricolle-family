from django.urls import path

from altered.views.home import home
from altered.views import game_form_view

app_name = "altered"

urlpatterns = [
    path("", home, name="home"),
    path('game/', game_form_view, name='game_form'),
]
