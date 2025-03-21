from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

class Login:
    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def user_logout(request):
        logout(request)
        return redirect("baby_name:login")
