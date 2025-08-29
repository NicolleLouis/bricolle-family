from django.urls import path

from agathe.views.home import HomeController
from agathe.views.pit_stop import PitStopController
from agathe.views.diaper_change import DiaperChangeController
from agathe.views.documents import DocumentController
from agathe.views.vitamin_intake import VitaminIntakeController
from agathe.views.bath import BathController
from agathe.views.aspirin_intake import AspirinIntakeController

app_name = "agathe"

urlpatterns = [
    path("", HomeController.home, name="home"),
    path("pit_stop/", PitStopController.pit_stop, name="pit_stop"),
    path("pit_stop/<int:pk>/finish/", PitStopController.finish, name="pit_stop_finish"),
    path(
        "pit_stop/finish_current/",
        PitStopController.finish_current,
        name="pit_stop_finish_current",
    ),
    path("diaper_change/", DiaperChangeController.diaper_change, name="diaper_change"),
    path("vitamin_intake/", VitaminIntakeController.create, name="vitamin_intake"),
    path("bath/", BathController.create, name="bath"),
    path("aspirin_intake/", AspirinIntakeController.create, name="aspirin_intake"),
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
