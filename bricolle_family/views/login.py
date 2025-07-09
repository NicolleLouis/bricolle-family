from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.shortcuts import redirect, render

class Login:
    @staticmethod
    def user_login(request):
        if request.method == "POST":
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect("home")
        else:
            form = AuthenticationForm()
        return render(request, "bricolle_family/login.html", {"form": form})

    @staticmethod
    def user_logout(request):
        logout(request)
        return redirect("login")
