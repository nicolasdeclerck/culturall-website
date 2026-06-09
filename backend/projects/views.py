from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_safe

from .models import ProjectPage, ProjectsIndexPage


@require_safe
def projects_index(request):
    """Liste des projets (page complète, ou partial HTMX si filtre par tag)."""
    page = ProjectsIndexPage.objects.live().first()
    if page is None:
        raise Http404("Page projets introuvable")
    return page.serve(request)


@require_safe
def project_page(request, slug):
    """Détail d'un projet publié, rendu via son template Wagtail natif."""
    project = get_object_or_404(ProjectPage.objects.live().public(), slug=slug)
    return project.serve(request)
