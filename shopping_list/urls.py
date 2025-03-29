from django.urls import path

from shopping_list.views.cart import cart
from shopping_list.views.home import home
from shopping_list.views.list import shopping_list
from shopping_list.views.login import Login
from shopping_list.views.meal import meal

app_name = "shopping_list"

urlpatterns = [
    path("", home, name="home"),
    path("cart/", cart, name="cart"),
    path("login/", Login.user_login, name="login"),
    path("logout/", Login.user_logout, name="logout"),
    path("meal/", meal, name="meal"),
    path("register/", Login.register, name="register"),
    path("shopping_list", shopping_list, name="list"),
]
