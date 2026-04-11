from django.http import JsonResponse
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import Article


@require_GET
def article_list(request):
    """Return published articles as JSON, with optional limit and tag filters."""
    articles = Article.objects.filter(live=True).prefetch_related("tags").select_related("illustration")

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

    data = [
        {
            "id": article.pk,
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
            "created_at": article.created_at.isoformat(),
        }
        for article in articles
    ]
    return JsonResponse(data, safe=False)
