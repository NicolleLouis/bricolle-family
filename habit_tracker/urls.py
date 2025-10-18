from django.urls import path

from habit_tracker.views.calendar import calendar_view
from habit_tracker.views.day import day_create
from habit_tracker.views.objectives import objectives_overview
from habit_tracker.views.home import home

app_name = "habit_tracker"

urlpatterns = [
    path("", calendar_view, name="calendar"),
    path("home/", home, name="home"),
    path("calendar/", calendar_view, name="calendar"),
    path("objectives/", objectives_overview, name="objectives"),
    path("days/new/", day_create, name="day_create"),
]
