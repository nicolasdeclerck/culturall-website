from django.conf import settings


def turnstile(request):
    """Expose la clé publique Turnstile aux templates (chaîne vide si non configurée)."""
    return {"TURNSTILE_SITE_KEY": settings.TURNSTILE_SITE_KEY}
