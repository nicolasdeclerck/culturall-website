from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page

MAX_FEATURED_PROJECTS = 3


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
    featured = models.BooleanField("À la une", default=False)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        FieldPanel("year"),
        FieldPanel("video_duration"),
        FieldPanel("credits"),
        FieldPanel("tags"),
        FieldPanel("youtube_url"),
        FieldPanel("thumbnail"),
        FieldPanel("featured"),
    ]

    parent_page_types = ["projects.ProjectsIndexPage"]
    subpage_types = []

    preview_modes = []

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def clean(self):
        super().clean()
        if self.featured:
            qs = ProjectPage.objects.filter(featured=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.count() >= MAX_FEATURED_PROJECTS:
                raise ValidationError(
                    {"featured": f"Il ne peut y avoir plus de {MAX_FEATURED_PROJECTS} projets à la une."}
                )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
