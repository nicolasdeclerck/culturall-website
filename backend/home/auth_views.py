import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from wagtail.models import Site

from site_settings.models import SiteSettings


def auth_check(request):
    """Returns authentication status, whether auth is required, and logo URL."""
    site = Site.find_for_request(request)
    settings = SiteSettings.for_site(site)

    logo_url = None
    if settings.logo:
        logo_url = settings.logo.get_rendition("max-300x80").url

    return JsonResponse({
        "authenticated": request.user.is_authenticated,
        "require_authentication": settings.require_authentication,
        "logo_url": logo_url,
    })


@csrf_exempt
@require_POST
def auth_login(request):
    """Authenticates a user with username and password."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "JSON invalide."}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse(
            {"error": "Nom d'utilisateur et mot de passe requis."},
            status=400,
        )

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"message": "Connexion réussie."})

    return JsonResponse({"error": "Identifiants invalides."}, status=401)


@csrf_exempt
@require_POST
def auth_logout(request):
    """Logs out the current user."""
    logout(request)
    return JsonResponse({"message": "Déconnexion réussie."})
