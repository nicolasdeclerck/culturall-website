from django.db import models
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting


@register_setting
class SiteSettings(BaseSiteSetting):
    require_authentication = models.BooleanField(
        default=True,
        verbose_name="Authentification requise",
        help_text=(
            "Si activé, le site n'est accessible qu'aux utilisateurs connectés. "
            "Les comptes sont gérés via l'admin Wagtail."
        ),
    )

    class Meta:
        verbose_name = "Paramètres du site"
        verbose_name_plural = "Paramètres du site"
