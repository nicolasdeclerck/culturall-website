from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet


@register_snippet
class NetworkMember(models.Model):
    name = models.CharField("Nom", max_length=255)
    member_type = models.CharField("Type", max_length=100)
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Logo",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("member_type"),
        FieldPanel("logo"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name = "Membre du réseau"
        verbose_name_plural = "Membres du réseau"

    def __str__(self):
        return self.name
