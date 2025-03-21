import random

from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Exists, OuterRef

from baby_name.constants.name_choice import NameChoice
from .models import Name, Evaluation

def index(request):
    name_coup_de_coeur_list = Name.objects.filter(evaluation__score="coup_de_coeur").distinct()
   
    context = {
        "name_coup_de_coeur_list": name_coup_de_coeur_list
    }
    return render(request, "baby_name/index.html", context)

def results(request):
    name_coup_de_coeur_list_boys = Name.objects.filter(
        evaluation__score="coup_de_coeur", 
        evaluation__user=request.user,
        sex=False
    ).distinct()

    name_coup_de_coeur_list_girls= Name.objects.filter(
        evaluation__score="coup_de_coeur", 
        evaluation__user=request.user,
        sex=True
    ).distinct()

    name_yes_list_boys = Name.objects.filter(
        evaluation__score="oui", 
        evaluation__user=request.user,
        sex=False
    ).distinct()
    name_yes_list_girls = Name.objects.filter(
        evaluation__score="oui", 
        evaluation__user=request.user,
        sex=True
    ).distinct()
    
    context = {
        "name_coup_de_coeur_list_boys": name_coup_de_coeur_list_boys,
        "name_coup_de_coeur_list_girls": name_coup_de_coeur_list_girls,
        "name_yes_list_boys": name_yes_list_boys,
        "name_yes_list_girls": name_yes_list_girls,
    }
    return render(request, "baby_name/results.html", context)

def interface(request):
    if request.method == "POST":
        gender_filter = request.POST.get("gender", "all")
        request.session["gender_filter"] = gender_filter  
    else:
        gender_filter = request.session.get("gender_filter", "all") 

    #Sort the available names
    if gender_filter == "boys":
        names_left = Name.objects.filter(sex=False).exclude(evaluation__user=request.user) 
    elif gender_filter == "girls":
        names_left = Name.objects.filter(sex=True).exclude(evaluation__user=request.user) 
    else:
        names_left = Name.objects.exclude(evaluation__user=request.user) 

    if names_left.exists(): 
        random_name = random.choice(names_left)
        random_id=random_name.id
        name = get_object_or_404(Name, id=random_id)
    else: 
        name = None

    choices = NameChoice.choices
    context = {
        "name": name,
        "choices": choices, 
        "gender_filter": gender_filter 
    }
    return render(request, "baby_name/interface.html", context)

def vote(request):
    name_id = request.POST.get('name_id')
    score = request.POST.get('score')
    gender_filter = request.POST.get("gender", "all")
    
    name = get_object_or_404(Name, id = name_id)
    request.session["gender_filter"] = gender_filter
    
    if score:
        evaluation, _created = Evaluation.objects.get_or_create(
            name=name,
            user=request.user,
        )
        evaluation.score = score
        evaluation.save()
        return redirect('baby_name:interface')
    else:
        return redirect("baby_name:interface")
    
def ranking(request):
    #Randomly decide boy or girl
    sex_to_rank = random.choice([True, False])
    
    #Get an appropriate list of available names (ranked by user & one "oui" or "coup_de_coeur")
    user_evaluated_names = Name.objects.filter(
        sex=sex_to_rank, 
        evaluation__user=request.user
    ).distinct()

    ranking_names = user_evaluated_names.filter(
        Exists(
            Evaluation.objects.filter(
                name=OuterRef('pk'),
                score__in=["oui", "coup_de_coeur"]
            )
        )
    )

    #Randomly picks two names
    if ranking_names.exists(): 
        random_name_1 = random.choice(ranking_names)
        ranking_names = ranking_names.exclude(id=random_name_1.id)
        random_name_2 = random.choice(ranking_names)
        (random_id_1, random_id_2) = (random_name_1.id,random_name_2.id)
        name_1 = get_object_or_404(Name, id=random_id_1)
        name_2 = get_object_or_404(Name, id=random_id_2)
    else: 
        name_1 = None
        name_2 = None 

    #Context
    context = {
        "name_1": name_1,
        "name_2": name_2,
    }
    return render(request, "baby_name/ranking.html", context)

def ranking_vote(request):
    winner_id = request.POST.get('winner_id')
    loser_id = request.POST.get('loser_id')

    winner_eval = get_object_or_404(Evaluation, name__id = winner_id, user=request.user)
    loser_eval = get_object_or_404(Evaluation, name__id = loser_id, user=request.user)

    winner_eval.win_game(loser_eval)
    loser_eval.lose_game(winner_eval)

    return redirect('baby_name:ranking')


def leaderboard(request):
    all_users = User.objects.all()
    rankings_boys = {}
    rankings_girls = {}

    for username in all_users:
        user = User.objects.filter(username=username).first()
        rankings_boys[username] = Evaluation.objects.filter(
                user=user,
                name__sex=False,
                nb_duels__gte=3
            ).order_by('-elo')[:15]
    
        rankings_girls[username] = Evaluation.objects.filter(
            user=user,
            name__sex=True,
            nb_duels__gte=3
        ).order_by('-elo')[:15]

    context = {
        "rankings_boys" : rankings_boys,
        "rankings_girls" :rankings_girls,
    }
    
    return render(request, "baby_name/leaderboard.html", context)


#Register system
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("baby_name")
    else:
        form = UserCreationForm()
    return render(request, "baby_name/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("baby_name:index")
    else:
        form = AuthenticationForm()
    return render(request, "baby_name/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("baby_name:login")
