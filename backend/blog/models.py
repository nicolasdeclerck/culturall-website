from django.db import models
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Page
from wagtail_headless_preview.models import HeadlessPreviewMixin


class ArticlePageTag(TaggedItemBase):
    content_object = ParentalKey(
        "blog.ArticlePage",
        on_delete=models.CASCADE,
        related_name="tagged_items",
    )


class BlogIndexPage(Page):
    """Page de listing du blog. Parent unique des ArticlePage."""

    intro = RichTextField("Introduction", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = ["blog.ArticlePage"]
    max_count = 1

    # Pas de preview headless pour la page de listing
    preview_modes = []

    class Meta:
        verbose_name = "Index de blog"


class ArticlePage(HeadlessPreviewMixin, Page):
    """Article de blog publié dans l'arbre Wagtail."""

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
    tags = ClusterTaggableManager(
        through=ArticlePageTag,
        blank=True,
        verbose_name="Tags",
    )

    content_panels = Page.content_panels + [
        FieldPanel("summary"),
        FieldPanel("content"),
        FieldPanel("illustration"),
        FieldPanel("tags"),
    ]

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    class Meta:
        verbose_name = "Article"
        verbose_name_plural = "Articles"
