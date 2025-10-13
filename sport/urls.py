from django.urls import path

from sport.views.configuration import configuration
from sport.views.home import home
from sport.views.planning import planning
from sport.views.session import session_create, session_delete

app_name = "sport"

urlpatterns = [
    path("", home, name="home"),
    path("planification/", planning, name="planning"),
    path("configuration/", configuration, name="configuration"),
    path("sessions/new/", session_create, name="session_create"),
    path("sessions/<int:pk>/delete/", session_delete, name="session_delete"),
]
