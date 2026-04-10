from django.http import JsonResponse
from wagtail.models import Site

from site_settings.models import SiteSettings


class LoginRequiredMiddleware:
    """
    When SiteSettings.require_authentication is True, rejects unauthenticated
    requests to API endpoints with a 401 response.

    Excluded paths (always allowed):
    - /admin/        → Wagtail admin (has its own auth)
    - /django-admin/ → Django admin (has its own auth)
    - /api/auth/     → Auth endpoints (must be accessible to log in)
    - /static/       → Static files
    - /media/        → Media files
    """

    EXCLUDED_PREFIXES = (
        "/admin/",
        "/django-admin/",
        "/api/auth/",
        "/documents/",
        "/static/",
        "/media/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not self._is_excluded(request.path):
            site = Site.find_for_request(request)
            settings = SiteSettings.for_site(site)
            if settings.require_authentication:
                return JsonResponse(
                    {"error": "Authentification requise."},
                    status=401,
                )

        return self.get_response(request)

    def _is_excluded(self, path):
        return any(path.startswith(prefix) for prefix in self.EXCLUDED_PREFIXES)
