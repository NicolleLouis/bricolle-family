from django.urls import path

from babyberon.views.home import home
from babyberon.views.login import Login

app_name = "babyberon"

urlpatterns = [
    path("", home, name="home"),
    path('login/', Login.user_login, name='login'),
    path('logout/', Login.user_logout, name='logout'),
]
