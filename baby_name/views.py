import random
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import get_object_or_404, render, redirect

# Create your views here.
from django.http import HttpResponse

from .models import Name, Evaluation, NameChoice, User


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
        Evaluation.objects.create(
                name=name,
                user=request.user,
                score=score
            )
        return redirect('baby_name:interface')
    else:
        return redirect("baby_name:interface")
    
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
            return redirect("baby_name:index")  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, "baby_name/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("baby_name:login")