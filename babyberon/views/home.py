from django.shortcuts import render

from babyberon.models import BabyBottle


def home(request):
    baby_bottles = BabyBottle.objects.all().order_by('-created_at')[:5]
    return render(request, "babyberon/home.html", {'baby_bottles': baby_bottles})
