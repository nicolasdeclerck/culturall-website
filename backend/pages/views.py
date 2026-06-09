from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from .models import StaticContentPage


@require_safe
def static_page_html(request, slug):
    """Rend une StaticContentPage côté serveur via son template Wagtail natif.

    Sert toutes les pages statiques publiées (À propos, Mentions légales, …).
    Le rendu passe par ``Page.serve()``, donc par la résolution de template
    native de Wagtail (``pages/static_content_page.html``) et ``get_context()``.
    La preview rédactionnelle est native (Wagtail rend le même template).
    """
    page = get_object_or_404(StaticContentPage.objects.live(), slug=slug)
    return page.serve(request)
