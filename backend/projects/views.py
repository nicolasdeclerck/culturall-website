from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import ProjectPage


def _base_queryset():
    """Return the base ProjectPage queryset with common prefetches."""
    return (
        ProjectPage.objects.live()
        .order_by("-first_published_at")
        .prefetch_related("tags")
        .select_related("thumbnail")
    )


def _serialize_project(request, project):
    return {
        "id": project.pk,
        "slug": project.slug,
        "title": project.title,
        "description": expand_db_html(project.description) if project.description else "",
        "youtube_url": project.youtube_url,
        "tags": [tag.name for tag in project.tags.all()],
        "thumbnail_url": (
            request.build_absolute_uri(
                project.thumbnail.get_rendition("fill-600x400").url
            )
            if project.thumbnail
            else None
        ),
        "year": project.year,
        "video_duration": project.video_duration,
        "credits": expand_db_html(project.credits) if project.credits else "",
    }


def _serialize_projects(request, projects):
    return [_serialize_project(request, p) for p in projects]


@require_GET
def project_list(request):
    """Return all live projects as JSON."""
    return JsonResponse(_serialize_projects(request, _base_queryset()), safe=False)


@require_GET
def project_featured(request):
    """Return featured live projects as JSON."""
    return JsonResponse(
        _serialize_projects(request, _base_queryset().filter(featured=True)),
        safe=False,
    )


@require_GET
def project_detail(request, slug):
    """Return a single live project by slug."""
    try:
        project = _base_queryset().get(slug=slug)
    except ProjectPage.DoesNotExist:
        raise Http404
    return JsonResponse(_serialize_project(request, project))
