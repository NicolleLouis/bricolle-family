from django.urls import path

from finance_simulator.views.home import home
from finance_simulator.views.documents import ideas

app_name = "finance_simulator"

urlpatterns = [
    path("", home, name="home"),
    path("ideas/", ideas, name="ideas"),
]
