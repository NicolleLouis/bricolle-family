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
    return render(request, "helpinglouis/index.html", context) 

def results(request):
    name_coup_de_coeur_list = Name.objects.filter(evaluation__score="coup_de_coeur", evaluation__user=request.user).distinct()
    name_yes_list = Name.objects.filter(evaluation__score="yes", evaluation__user=request.user).distinct()
    
    context = {
        "name_coup_de_coeur_list": name_coup_de_coeur_list,
        "name_yes_list": name_yes_list,
    }
    return render(request, "helpinglouis/results.html", context) 

def interface(request):

    if request.method == "POST":
        gender_filter = request.POST.get("gender", "all")
        request.session["gender_filter"] = gender_filter  
    else:
        gender_filter = request.session.get("gender_filter", "all") 

    if gender_filter == "boys":
        names_left = Name.objects.filter(evaluation__isnull=True, sex=False) 
    elif gender_filter == "girls":
        names_left = Name.objects.filter(evaluation__isnull=True, sex=True)  
    else:
        names_left = Name.objects.filter(evaluation__isnull=True) 


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
    return render(request, "helpinglouis/interface.html", context)

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
        return redirect('helpinglouis:interface')
    else:
        return redirect("helpinglouis:interface")
    
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect("helpinglouis")  
    else:
        form = UserCreationForm()
    return render(request, "helpinglouis/register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("helpinglouis:index")  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, "helpinglouis/login.html", {"form": form})

def user_logout(request):
    logout(request)
    return redirect("helpinglouis:login")