from django.shortcuts import render


def back_to_the_dawn(request):
    return render(request, 'games_collection/back_to_the_dawn.html')
