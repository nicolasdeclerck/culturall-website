from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import StaticContentPage


def _serialize(page):
    return {
        "slug": page.slug,
        "title": page.title,
        "body": expand_db_html(page.body) if page.body else "",
    }


@require_GET
def static_page_detail(request, slug):
    """Return a published static page as JSON."""
    try:
        page = StaticContentPage.objects.live().get(slug=slug)
    except StaticContentPage.DoesNotExist as exc:
        raise Http404("Page introuvable") from exc

    return JsonResponse(_serialize(page))


@require_GET
def static_page_preview_draft(request):
    """Retourne les données brouillon d'une StaticContentPage pour la preview headless.

    Authentifié par token signé (créé par wagtail-headless-preview lors du clic Aperçu).
    Le token fait office de credential — aucune session Django requise.
    """
    from django.core.signing import BadSignature

    token = request.GET.get("token")
    if not token:
        raise Http404("Token manquant")

    try:
        page = StaticContentPage.get_page_from_preview_token(token)
    except BadSignature:
        raise Http404("Token invalide")

    if page is None:
        raise Http404("Token introuvable ou expiré")

    return JsonResponse(_serialize(page))
