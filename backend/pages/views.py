from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
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
def static_page_html(request, slug):
    """Rend une StaticContentPage côté serveur via son template Wagtail natif.

    Sert toutes les pages statiques publiées (À propos, Mentions légales, …).
    Le rendu passe par ``Page.serve()``, donc par la résolution de template
    native de Wagtail (``pages/static_content_page.html``) et ``get_context()``.
    La preview rédactionnelle est native (Wagtail rend le même template).
    """
    page = get_object_or_404(StaticContentPage.objects.live(), slug=slug)
    return page.serve(request)
