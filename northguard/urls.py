from django.urls import path

from northguard.views.home import home

app_name = 'northguard'

urlpatterns = [
    path('', home, name='home'),
]
