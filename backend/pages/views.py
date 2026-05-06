from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import StaticContentPage


@require_GET
def static_page_detail(request, slug):
    """Return a published static page as JSON."""
    try:
        page = StaticContentPage.objects.live().get(slug=slug)
    except StaticContentPage.DoesNotExist as exc:
        raise Http404("Page introuvable") from exc

    return JsonResponse(
        {
            "slug": page.slug,
            "title": page.title,
            "body": expand_db_html(page.body) if page.body else "",
        }
    )
