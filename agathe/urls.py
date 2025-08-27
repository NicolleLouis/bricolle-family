from django.urls import path

from agathe.views.pit_stop import PitStopController
from agathe.views.diaper_change import DiaperChangeController

app_name = "agathe"

urlpatterns = [
    path("pit_stop/", PitStopController.pit_stop, name="pit_stop"),
    path("pit_stop/<int:pk>/finish/", PitStopController.finish, name="pit_stop_finish"),
    path("diaper_change/", DiaperChangeController.diaper_change, name="diaper_change"),
]
