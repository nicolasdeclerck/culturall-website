from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images import get_image_model_string


@register_setting
class SiteSettings(BaseSiteSetting):
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Logo du site",
        help_text=(
            "Logo affiché dans l'en-tête à la place du titre textuel. "
            "Formats recommandés : PNG ou SVG, max 500 Ko."
        ),
    )

    require_authentication = models.BooleanField(
        default=True,
        verbose_name="Authentification requise",
        help_text=(
            "Si activé, le site n'est accessible qu'aux utilisateurs connectés. "
            "Les comptes sont gérés via l'admin Wagtail."
        ),
    )

    panels = [
        FieldPanel("logo"),
        FieldPanel("require_authentication"),
    ]

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
