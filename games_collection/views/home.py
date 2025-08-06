from django.shortcuts import redirect


def home(request):
    return redirect('games_collection:back_to_the_dawn')
