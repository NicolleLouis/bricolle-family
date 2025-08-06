from django.urls import path

from games_collection.views.home import home
from games_collection.views.back_to_the_dawn import back_to_the_dawn

app_name = 'games_collection'

urlpatterns = [
    path('', home, name='home'),
    path('back_to_the_dawn/', back_to_the_dawn, name='back_to_the_dawn'),
]
