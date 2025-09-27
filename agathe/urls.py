from django.urls import path

from agathe.views.home import HomeController
from agathe.views.pit_stop import PitStopController
from agathe.views.diaper_change import DiaperChangeController
from agathe.views.documents import DocumentController
from agathe.views.vitamin_intake import VitaminIntakeController
from agathe.views.bath import BathController

app_name = "agathe"

urlpatterns = [
    path("", HomeController.home, name="home"),
    path("pit_stop/", PitStopController.pit_stop, name="pit_stop"),
    path("pit_stop/stats/", PitStopController.stats, name="pit_stop_stats"),
    path("diaper_change/", DiaperChangeController.diaper_change, name="diaper_change"),
    path(
        "diaper_change/quick/",
        DiaperChangeController.quick,
        name="diaper_change_quick",
    ),
    path("vitamin_intake/", VitaminIntakeController.create, name="vitamin_intake"),
    path("bath/", BathController.create, name="bath"),
    path("question/", DocumentController.question_to_ask, name="question_to_ask"),
    path(
        "next_evolution_milestone/",
        DocumentController.next_evolution_milestone,
        name="next_evolution_milestone",
    ),
    path(
        "website_ideas/",
        DocumentController.website_ideas,
        name="website_ideas",
    ),
]
