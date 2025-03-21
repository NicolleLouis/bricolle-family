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
    elo = models.IntegerField(default=1000)
    nb_duels = models.IntegerField(default=0)

    class Meta:
        unique_together = ('name', 'user')

    def __str__(self):
       return f"Note {self.user.username} -> {self.name}"

    def update_elo_against(self, opponent, k=20):
        diff = opponent.elo - self.elo
        expected = 1 / (1 + 10 ** (diff / 400))
        delta = round(k * (1 - expected))

        self.elo += delta
        opponent.elo -= delta

        for eval in [self,opponent]:
            eval.nb_duels += 1
            eval.save()
