from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from .models import ArticlePage, BlogIndexPage


@require_safe
def blog_index(request):
    """Liste des articles (page complète, ou partial HTMX si filtre par tag)."""
    page = BlogIndexPage.objects.live().first()
    if page is None:
        raise Http404("Blog introuvable")
    return page.serve(request)


@require_safe
def article_page(request, slug):
    """Détail d'un article publié, rendu via son template Wagtail natif."""
    article = get_object_or_404(ArticlePage.objects.live().public(), slug=slug)
    return article.serve(request)
