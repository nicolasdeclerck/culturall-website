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

    def _published_articles(self):
        return (
            ArticlePage.objects.child_of(self)
            .live()
            .public()
            .prefetch_related("tags")
            .select_related("illustration")
            .order_by("-first_published_at")
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_articles = self._published_articles()
        current_tag = request.GET.get("tag") or None

        articles = all_articles.filter(tags__name=current_tag) if current_tag else all_articles

        context["articles"] = articles
        context["current_tag"] = current_tag
        # Tags utilisés par l'ensemble des articles publiés (indépendant du filtre).
        context["tags"] = sorted({tag.name for article in all_articles for tag in article.tags.all()})
        return context

    def get_template(self, request, *args, **kwargs):
        # En requête HTMX (filtre par tag), on ne renvoie que la liste à swapper.
        if getattr(request, "htmx", False):
            return "blog/_article_list.html"
        return super().get_template(request, *args, **kwargs)


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
