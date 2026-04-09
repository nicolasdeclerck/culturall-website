from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet


class ProjectTag(TaggedItemBase):
    content_object = ParentalKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


@register_snippet
class Project(ClusterableModel):
    title = models.CharField("Titre", max_length=255)
    description = models.TextField("Description", blank=True)
    youtube_url = models.URLField("Lien YouTube")
    tags = ClusterTaggableManager(
        through=ProjectTag,
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
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("tags"),
        FieldPanel("youtube_url"),
        FieldPanel("thumbnail"),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title
