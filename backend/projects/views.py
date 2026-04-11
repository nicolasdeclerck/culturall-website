from django.http import JsonResponse
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import Project


def _serialize_projects(request, projects):
    """Serialize a queryset of projects to a list of dicts."""
    return [
        {
            "id": project.pk,
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
        }
        for project in projects
    ]


@require_GET
def project_list(request):
    """Return all projects as JSON."""
    projects = Project.objects.prefetch_related("tags").select_related("thumbnail").all()
    return JsonResponse(_serialize_projects(request, projects), safe=False)


@require_GET
def project_featured(request):
    """Return featured projects as JSON."""
    projects = (
        Project.objects.filter(featured=True)
        .prefetch_related("tags")
        .select_related("thumbnail")
    )
    return JsonResponse(_serialize_projects(request, projects), safe=False)
