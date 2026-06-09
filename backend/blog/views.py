from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import ArticlePage, BlogIndexPage


def _serialize_article(request, article):
    return {
        "id": article.pk,
        "slug": article.slug,
        "title": article.title,
        "summary": article.summary,
        "content": expand_db_html(article.content) if article.content else "",
        "illustration_url": (
            request.build_absolute_uri(
                article.illustration.get_rendition("fill-800x500").url
            )
            if article.illustration
            else None
        ),
        "tags": [t.name for t in article.tags.all()],
        "created_at": article.first_published_at.isoformat() if article.first_published_at else "",
    }


def _published_articles():
    return (
        ArticlePage.objects.live()
        .public()
        .prefetch_related("tags")
        .select_related("illustration")
        .order_by("-first_published_at")
    )


@require_GET
def article_list(request):
    """Liste des articles publiés en JSON, avec filtres optionnels limit et tag."""
    articles = _published_articles()

    tag = request.GET.get("tag")
    if tag:
        articles = articles.filter(tags__name=tag)

    limit = request.GET.get("limit")
    if limit:
        try:
            limit_val = int(limit)
            if limit_val > 0:
                articles = articles[:limit_val]
        except (ValueError, TypeError):
            pass

    data = [_serialize_article(request, article) for article in articles]
    return JsonResponse(data, safe=False)


@require_GET
def article_detail(request, slug):
    """Détail d'un article publié, identifié par slug."""
    try:
        article = _published_articles().get(slug=slug)
    except ArticlePage.DoesNotExist as exc:
        raise Http404("Article introuvable") from exc

    return JsonResponse(_serialize_article(request, article))


@require_GET
def article_preview_draft(request):
    """Retourne les données brouillon d'un ArticlePage pour la preview headless.

    Authentifié par token signé (créé par wagtail-headless-preview lors du clic Aperçu).
    Le token fait office de credential — aucune session Django requise.
    """
    from django.core.signing import BadSignature

    token = request.GET.get("token")
    if not token:
        raise Http404("Token manquant")

    try:
        page = ArticlePage.get_page_from_preview_token(token)
    except BadSignature:
        raise Http404("Token invalide")

    if page is None:
        raise Http404("Token introuvable ou expiré")

    return JsonResponse(_serialize_article(request, page))


# ─── Rendu serveur (Phase 3) ───────────────────────────────────
# Routes explicites tant que le catch-all Wagtail global est désactivé
# (réactivation Phase 5). Le rendu passe par Page.serve() : BlogIndexPage
# gère le filtre par tag + le partial HTMX via get_context/get_template.


@require_GET
def blog_index(request):
    """Liste des articles (page complète, ou partial HTMX si filtre par tag)."""
    page = BlogIndexPage.objects.live().first()
    if page is None:
        raise Http404("Blog introuvable")
    return page.serve(request)


@require_GET
def article_page(request, slug):
    """Détail d'un article publié, rendu via son template Wagtail natif."""
    article = get_object_or_404(ArticlePage.objects.live().public(), slug=slug)
    return article.serve(request)
