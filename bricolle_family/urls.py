from django.contrib import admin
from django.urls import include, path

from bricolle_family.views import home

urlpatterns = [
    path("", home, name="home"),
    path("baby_name/", include("baby_name.urls")),
    path("shopping_list/", include("shopping_list.urls")),
    path('admin/', admin.site.urls),
    path('habit_tracker/', include("habit_tracker.urls")),
]
