from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from modelcluster.tags import ClusterTaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import DraftStateMixin, RevisionMixin
from wagtail.snippets.models import register_snippet


class ArticleTag(TaggedItemBase):
    content_object = ParentalKey(
        "blog.Article",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


@register_snippet
class Article(DraftStateMixin, RevisionMixin, ClusterableModel):
    title = models.CharField("Titre", max_length=255)
    tags = ClusterTaggableManager(
        through=ArticleTag,
        blank=True,
        verbose_name="Tags",
    )
    summary = models.TextField("Résumé", blank=True)
    content = RichTextField("Contenu")
    illustration = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Illustration",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("tags"),
        FieldPanel("summary"),
        FieldPanel("content"),
        FieldPanel("illustration"),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title
