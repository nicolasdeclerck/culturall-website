from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
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
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("tags"),
        FieldPanel("youtube_url"),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Projet"
        verbose_name_plural = "Projets"

    def __str__(self):
        return self.title
