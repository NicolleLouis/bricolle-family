from django.urls import path

from albion_online.views.home import home
from albion_online.views.leather_jacket import leather_jacket, leather_jacket_profitability
from albion_online.views.settings_page import settings_page

app_name = "albion_online"

urlpatterns = [
    path("", home, name="home"),
    path("leather_jacket/", leather_jacket, name="leather_jacket"),
    path("leather_jacket/profitable/", leather_jacket_profitability, name="leather_jacket_profitability"),
    path("settings/", settings_page, name="settings"),
]
