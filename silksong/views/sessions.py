from django.shortcuts import redirect, render

from silksong.constants import GameSessionType
from silksong.forms import (
    BossFightGameSessionForm,
    SpeedrunGameSessionForm,
    SteelSoulGameSessionForm,
)
from silksong.models import GameSession

RECENT_SESSIONS_LIMIT = 10


def _render_sessions_page(
    request,
    *,
    session_type,
    template_name,
    form_class,
    redirect_name,
    active_page,
    page_title,
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
    return _render_sessions_page(
        request,
        session_type=GameSessionType.BOSS_FIGHT,
        template_name="silksong/boss_fight_sessions.html",
        form_class=BossFightGameSessionForm,
        redirect_name="silksong:boss_fight_sessions",
        active_page="boss_fight",
        page_title="Boss Fight",
    )
