from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from bricolle_family import settings
from bricolle_family.views.home import home
from bricolle_family.views.login import Login

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("altered/", include("altered.urls")),
    path("baby_name/", include("baby_name.urls")),
    path("babyberon/", include("babyberon.urls")),
    path("login", Login.user_login, name="login"),
    path("logout", Login.user_logout, name="logout"),
    path("northguard/", include("northguard.urls")),
    path("shopping_list/", include("shopping_list.urls")),
    path("the_bazaar/", include("the_bazaar.urls")),
]

if settings.ENV == 'local':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
