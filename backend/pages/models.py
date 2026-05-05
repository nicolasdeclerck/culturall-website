from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import DraftStateMixin, RevisionMixin
from wagtail.snippets.models import register_snippet


class StaticPageSlug(models.TextChoices):
    MENTIONS_LEGALES = "mentions-legales", "Mentions légales"
    A_PROPOS = "a-propos", "À propos"


@register_snippet
class StaticPage(DraftStateMixin, RevisionMixin, models.Model):
    slug = models.SlugField(
        "Identifiant",
        max_length=64,
        unique=True,
        choices=StaticPageSlug.choices,
        help_text="Identifie la page côté frontend (ne pas modifier).",
    )
    title = models.CharField("Titre", max_length=255)
    body = RichTextField("Contenu", blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("slug", read_only=True),
        FieldPanel("title"),
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Page statique"
        verbose_name_plural = "Pages statiques"
        ordering = ["slug"]

    def __str__(self):
        return self.get_slug_display()
