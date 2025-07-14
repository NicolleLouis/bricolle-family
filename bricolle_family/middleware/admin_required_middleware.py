from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_PREFIXES = [
    "/baby_name/",
    settings.STATIC_URL,
    settings.MEDIA_URL,
]

EXEMPT_URLS = [
    reverse("login"),
    reverse("logout"),
    reverse("home"),
    reverse("games"),
    reverse("more"),
]


class AdminRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_staff:
            path = request.path_info
            if (
                not any(path.startswith(p) for p in EXEMPT_PREFIXES)
                and path not in EXEMPT_URLS
            ):
                return redirect("home")
        return self.get_response(request)
