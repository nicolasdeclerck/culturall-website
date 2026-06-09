from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from wagtail.rich_text import expand_db_html

from .models import ProjectPage, ProjectsIndexPage


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


@require_GET
def project_preview_draft(request):
    """Retourne les données brouillon d'un ProjectPage pour la preview headless.

    Authentifié par token signé (créé par wagtail-headless-preview lors du clic Aperçu).
    Le token fait office de credential — aucune session Django requise.
    """
    from django.core.signing import BadSignature

    token = request.GET.get("token")
    if not token:
        raise Http404("Token manquant")

    try:
        page = ProjectPage.get_page_from_preview_token(token)
    except BadSignature:
        raise Http404("Token invalide")

    if page is None:
        raise Http404("Token introuvable ou expiré")

    return JsonResponse(_serialize_project(request, page))


# ─── Rendu serveur (Phase 4) ───────────────────────────────────
# Routes explicites tant que le catch-all Wagtail global est désactivé
# (réactivation Phase 5). Rendu via Page.serve().


@require_GET
def projects_index(request):
    """Liste des projets (page complète, ou partial HTMX si filtre par tag)."""
    page = ProjectsIndexPage.objects.live().first()
    if page is None:
        raise Http404("Page projets introuvable")
    return page.serve(request)


@require_GET
def project_page(request, slug):
    """Détail d'un projet publié, rendu via son template Wagtail natif."""
    project = get_object_or_404(ProjectPage.objects.live().public(), slug=slug)
    return project.serve(request)
