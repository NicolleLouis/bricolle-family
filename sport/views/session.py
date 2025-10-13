from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from sport.forms.session import SessionForm
from sport.models import Session


def session_create(request):
    if request.method == "POST":
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse("sport:home"))
    else:
        form = SessionForm()
    return render(request, "sport/session_form.html", {"form": form})


def session_delete(request, pk):
    if request.method == "POST":
        session = get_object_or_404(Session, pk=pk)
        session.delete()
        year = request.POST.get("year")
        month = request.POST.get("month")
        redirect_url = reverse("sport:home")
        if year and month:
            redirect_url = f"{redirect_url}?year={year}&month={month}"
        return redirect(redirect_url)
    return redirect(reverse("sport:home"))
