from django.urls import path

from battery_simulator.views.home import home

app_name = "battery_simulator"

urlpatterns = [
    path("", home, name="home"),
]
