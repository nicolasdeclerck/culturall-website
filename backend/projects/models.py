import re

from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page

# Extrait l'ID d'une vidéo YouTube depuis les formats watch / youtu.be / embed / shorts.
_YOUTUBE_ID_RE = re.compile(
    r"(?:youtu\.be/|youtube\.com/(?:watch\?.*v=|embed/|shorts/))([a-zA-Z0-9_-]{11})"
)


class ProjectPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "projects.ProjectPage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class ProjectsIndexPage(Page):
    """Page de listing des projets. Parent unique des ProjectPage."""

    content_panels = Page.content_panels

    parent_page_types = ["home.HomePage"]
    subpage_types = ["projects.ProjectPage"]
    max_count = 1

    preview_modes = []

    class Meta:
        verbose_name = "Index des projets"

    def _published_projects(self):
        return (
            ProjectPage.objects.child_of(self)
            .live()
            .public()
            .prefetch_related("tags")
            .select_related("thumbnail")
            .order_by("-first_published_at")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_projects = self._published_projects()
        current_tag = request.GET.get("tag") or None

        projects = all_projects.filter(tags__name=current_tag) if current_tag else all_projects

        context["projects"] = projects
        context["current_tag"] = current_tag
        context["tags"] = sorted({tag.name for project in all_projects for tag in project.tags.all()})
        return context

    def get_template(self, request, *args, **kwargs):
        # En requête HTMX (filtre par tag), on ne renvoie que la grille à swapper.
        if getattr(request, "htmx", False):
            return "projects/_project_list.html"
        return super().get_template(request, *args, **kwargs)


class ProjectPage(Page):
    """Projet publié dans l'arbre Wagtail."""

    description = RichTextField("Description", blank=True)
    youtube_url = models.URLField("Lien YouTube")
    tags = ClusterTaggableManager(
        through=ProjectPageTag,
        blank=True,
        verbose_name="Tags",
    )
    thumbnail = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Miniature",
    )
    year = models.CharField("Année de création", max_length=20, blank=True)
    video_duration = models.CharField("Durée de la vidéo", max_length=50, blank=True)
    credits = RichTextField("Crédits", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("year"),
        FieldPanel("video_duration"),
        FieldPanel("credits"),
        FieldPanel("tags"),
        FieldPanel("youtube_url"),
        FieldPanel("thumbnail"),
    ]

    parent_page_types = ["projects.ProjectsIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    @property
    def youtube_id(self):
        """ID de la vidéo YouTube extrait de youtube_url (None si introuvable)."""
        if not self.youtube_url:
            return None
        match = _YOUTUBE_ID_RE.search(self.youtube_url)
        return match.group(1) if match else None
