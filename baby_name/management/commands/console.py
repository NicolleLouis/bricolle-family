import csv
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from baby_name.models import Name, Evaluation

class Command(BaseCommand):
    help = "Random stuff"

    def handle(self, *args, **kwargs):
        user = User.objects.get(username="Zozette")
        for name in Name.objects.all():
            Evaluation.objects.create(user=user, name=name, score="oui")

        print("Evaluations assigned successfully!")
