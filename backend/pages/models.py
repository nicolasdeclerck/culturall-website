from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail_headless_preview.models import HeadlessPreviewMixin


class StaticContentPage(HeadlessPreviewMixin, Page):
    """Page statique éditable depuis Wagtail (À propos, Mentions légales, etc.)."""

    body = RichTextField("Contenu", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
