from django.urls import path

from finance_simulator.views.home import home

app_name = "finance_simulator"

urlpatterns = [
    path("", home, name="home"),
]
