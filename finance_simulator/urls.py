from django.urls import path

from finance_simulator.views.home import default_simulation, home
from finance_simulator.views.documents import ideas

app_name = "finance_simulator"

urlpatterns = [
    path("", home, name="home"),
    path("default/", default_simulation, name="default_simulation"),
    path("ideas/", ideas, name="ideas"),
]
