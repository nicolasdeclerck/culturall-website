from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class StaticContentPage(Page):
    """Page statique éditable depuis Wagtail (À propos, Mentions légales, etc.)."""

    body = RichTextField("Contenu", blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    preview_modes = []

    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
