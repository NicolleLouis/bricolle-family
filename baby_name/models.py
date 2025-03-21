from django.contrib.auth import get_user_model
from django.db import models

from baby_name.enum import NameChoice

User = get_user_model()

class Name(models.Model):
    name = models.CharField(max_length=200)
    sex = models.BooleanField(
        help_text= "True for a girl"
    )

    def __str__(self):
       return self.name

class Evaluation(models.Model):
    name = models.ForeignKey(Name, on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    score = models.CharField(
        max_length=20,
        choices=NameChoice.choices,
        default=NameChoice.NON
    )