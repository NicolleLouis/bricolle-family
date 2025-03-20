from django.urls import path

from . import views

app_name = "baby_name"

urlpatterns = [
    path("", views.index, name="index"),
    path("interface/", views.interface, name="interface"),
    path("vote/", views.vote, name="vote"),
    path("results/", views.results, name="results"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
]