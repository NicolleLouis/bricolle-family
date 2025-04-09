from django.urls import path

from habit_tracker.views.bazaar import bazaar
from habit_tracker.views.home import home
from habit_tracker.views.login import Login

app_name = "habit_tracker"

urlpatterns = [
    path("", home, name="home"),
    path("bazaar", bazaar, name="bazaar"),
    path("login/", Login.user_login, name="login"),
    path("logout/", Login.user_logout, name="logout"),
    path("register/", Login.register, name="register"),
]
