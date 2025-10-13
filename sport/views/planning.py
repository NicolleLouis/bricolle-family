from datetime import timedelta

from django.shortcuts import render
from django.utils import timezone

from sport.forms.planning import PlanningForm
from sport.models import Session


def planning(request):
    created_sessions = []
    skipped_dates = []

    if request.method == "POST":
        form = PlanningForm(request.POST)
        if form.is_valid():
            training = form.cleaned_data["training"]
            weekday = int(form.cleaned_data["weekday"])
            start_date = form.cleaned_data["start_date"]
            weeks_count = form.cleaned_data["weeks_count"]

            first_session_date = _first_matching_weekday(start_date, weekday)

            for week_index in range(weeks_count):
                target_date = first_session_date + timedelta(weeks=week_index)
                session, created = Session.objects.get_or_create(
                    training=training, date=target_date
                )
                if created:
                    created_sessions.append(session)
                else:
                    skipped_dates.append(target_date)

            form = PlanningForm()
    else:
        form = PlanningForm(
            initial={
                "start_date": timezone.now().date(),
            }
        )

    context = {
        "form": form,
        "created_sessions": created_sessions,
        "skipped_dates": skipped_dates,
    }
    return render(request, "sport/planning.html", context)


def _first_matching_weekday(start_date, weekday):
    delta = (weekday - start_date.weekday()) % 7
    return start_date + timedelta(days=delta)
