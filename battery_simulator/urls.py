from django.urls import path

from babyberon.views.home import home
from babyberon.views.baby_bottle import BabyBottleController

app_name = "battery_simulator"

urlpatterns = [
    path("", home, name="home"),
]
