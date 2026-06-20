from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from home.blocks import CustomSectionBlock


class StaticContentPage(Page):
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


class FlexiblePage(Page):
    """Page « flexible » construite à base de blocs StreamField.

    Pensée pour publier du contenu quand le design n'est pas encore figé :
    plutôt que de créer un gabarit dédié, l'éditeur empile librement les blocs
    disponibles (titres, textes riches, images, grilles de cartes, boutons,
    vidéos) depuis l'admin Wagtail. On réutilise la même palette de blocs que
    la « Section personnalisable » de la HomePage (`home.blocks`) pour profiter
    de ses templates et de son style déjà en place.
    """

    body = StreamField(
        CustomSectionBlock(),
        blank=True,
        verbose_name="Contenu",
        help_text="Empilez les blocs souhaités, dans l'ordre voulu.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    parent_page_types = ["home.HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Page flexible"
        verbose_name_plural = "Pages flexibles"
