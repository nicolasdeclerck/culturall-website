import json

from django.http import JsonResponse

from .models import Project


def project_list(request):
    """Return all projects as JSON."""
    projects = Project.objects.prefetch_related("tags").all()
    data = [
        {
            "id": project.pk,
            "title": project.title,
            "description": project.description,
            "youtube_url": project.youtube_url,
            "tags": [tag.name for tag in project.tags.all()],
        }
        for project in projects
    ]
    return JsonResponse(data, safe=False)
