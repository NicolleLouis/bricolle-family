from django.urls import path

from finance_simulator.views.home import (
    default_simulation,
    home,
    open_simulation,
    save_simulation,
)
from finance_simulator.views.documents import ideas

app_name = "finance_simulator"

urlpatterns = [
    path("", home, name="home"),
    path("default/", default_simulation, name="default_simulation"),
    path("simulation/<int:pk>/", open_simulation, name="open_simulation"),
    path("save/", save_simulation, name="save_simulation"),
    path("ideas/", ideas, name="ideas"),
]
