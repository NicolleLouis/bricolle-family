from django.urls import path

from chess.views.home import home
from chess.views.training_session import TrainingSessionController

app_name = 'chess'

urlpatterns = [
    path('', home, name='home'),
    path('training/add/', TrainingSessionController.add_training, name='training_add'),
    path('trainings/', TrainingSessionController.list_trainings, name='training_list'),
]
