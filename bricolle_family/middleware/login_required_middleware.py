from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

EXEMPT_URLS = [
    reverse('login'),
    reverse('admin:login'),
]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [reverse(url) for url in settings.LOGIN_EXEMPT_URLS]


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            path = request.path_info
            if not any(path.startswith(url) for url in EXEMPT_URLS):
                return redirect('%s?next=%s' % (reverse('login'), path))
        return self.get_response(request)
