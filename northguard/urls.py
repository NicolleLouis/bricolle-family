from django.urls import path

from northguard.views.build_order import BuildOrderController
from northguard.views.home import home

app_name = 'northguard'

urlpatterns = [
    path('', home, name='home'),
    path('build_orders', BuildOrderController.index, name='build_order_index'),
    path("build_order/<int:build_order_id>/edit", BuildOrderController.edit, name="build_order_edit"),
]
