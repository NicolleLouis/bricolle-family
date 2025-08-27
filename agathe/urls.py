from django.urls import path

from agathe.views.pit_stop import PitStopController

app_name = "agathe"

urlpatterns = [
    path("pit_stop/", PitStopController.pit_stop, name="pit_stop"),
]
