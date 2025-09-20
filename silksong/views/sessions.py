from django.db.models import Min
from django.shortcuts import redirect, render
from django.utils import timezone

from silksong.constants import Boss, GameSessionType
from silksong.forms import (
    BossFightGameSessionForm,
    SpeedrunGameSessionForm,
    SteelSoulGameSessionForm,
)
from silksong.models import GameSession

RECENT_SESSIONS_LIMIT = 10
BOSS_RECENT_TRIES_LIMIT = 5


def _format_time_since(datetime_value):
    if datetime_value is None:
        return None
    now = timezone.now()
    if datetime_value > now:
        return "Moins d'un jour"
    delta = now - datetime_value
    days = delta.days
    periods = [
        (365, "an", "ans"),
        (30, "mois", "mois"),
        (7, "semaine", "semaines"),
        (1, "jour", "jours"),
    ]
    for unit_days, singular, plural in periods:
        if days >= unit_days:
            value = days // unit_days
            label = singular if value == 1 else plural
            return f"{value} {label}"
    return "Moins d'un jour"


def _render_sessions_page(
    request,
    *,
    session_type,
    template_name,
    form_class,
    redirect_name,
    active_page,
    page_title,
    extra_context=None,
):
    sessions = (
        GameSession.objects.filter(type=session_type)
        .order_by("-created_at")[:RECENT_SESSIONS_LIMIT]
    )
    form = form_class(request.POST or None)
    show_modal = False

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect(redirect_name)
        show_modal = True

    context = {
        "sessions": sessions,
        "form": form,
        "limit": RECENT_SESSIONS_LIMIT,
        "active_page": active_page,
        "page_title": page_title,
        "show_modal": show_modal,
    }
    if extra_context:
        context.update(extra_context)
    return render(request, template_name, context)


def speedrun_sessions(request):
    return _render_sessions_page(
        request,
        session_type=GameSessionType.SPEEDRUN,
        template_name="silksong/speedrun_sessions.html",
        form_class=SpeedrunGameSessionForm,
        redirect_name="silksong:speedrun_sessions",
        active_page="speedrun",
        page_title="Speedrun",
    )


def steel_soul_sessions(request):
    return _render_sessions_page(
        request,
        session_type=GameSessionType.STEEL_SOUL,
        template_name="silksong/steel_soul_sessions.html",
        form_class=SteelSoulGameSessionForm,
        redirect_name="silksong:steel_soul_sessions",
        active_page="steel_soul",
        page_title="Steel Soul",
    )


def boss_fight_sessions(request):
    boss_stats = []
    base_queryset = GameSession.objects.filter(type=GameSessionType.BOSS_FIGHT)
    for boss_value, boss_label in Boss.choices:
        boss_queryset = base_queryset.filter(boss=boss_value)
        ordered_sessions = boss_queryset.order_by("-created_at")
        last_session = ordered_sessions.first()
        recent_sessions = list(ordered_sessions[:BOSS_RECENT_TRIES_LIMIT])
        recent_deaths = [
            session.death_number
            for session in recent_sessions
            if session.death_number is not None
        ]
        average_recent_deaths = (
            sum(recent_deaths) / len(recent_deaths) if recent_deaths else None
        )
        best_recent = min(recent_deaths) if recent_deaths else None
        worst_recent = max(recent_deaths) if recent_deaths else None
        best_all_time = boss_queryset.filter(death_number__isnull=False).aggregate(
            Min("death_number")
        )["death_number__min"]
        time_since_last_try = (
            _format_time_since(last_session.created_at) if last_session else None
        )
        boss_stats.append(
            {
                "name": boss_label,
                "average_recent_deaths": average_recent_deaths,
                "best_all_time": best_all_time,
                "best_recent": best_recent,
                "worst_recent": worst_recent,
                "time_since_last_try": time_since_last_try,
            }
        )

    extra_context = {
        "boss_stats": boss_stats,
        "recent_try_limit": BOSS_RECENT_TRIES_LIMIT,
    }
    return _render_sessions_page(
        request,
        session_type=GameSessionType.BOSS_FIGHT,
        template_name="silksong/boss_fight_sessions.html",
        form_class=BossFightGameSessionForm,
        redirect_name="silksong:boss_fight_sessions",
        active_page="boss_fight",
        page_title="Boss Fight",
        extra_context=extra_context,
    )
