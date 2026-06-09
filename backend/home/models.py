"""
Home app — point d'entrée Wagtail.

La `HomePage` est créée par la data migration `0003_seed_home_page` et sert
de racine à l'arbre Wagtail (parent direct de `BlogIndexPage` et, à terme,
des autres pages d'accueil de section). Le `Site` Wagtail par défaut pointe
sur cette `HomePage`.

Le rendu HTML est fait par le frontend Next.js : le catch-all Wagtail reste
désactivé dans `config/urls.py` tant que la preview headless (#121) n'est
pas en place.
"""

from functools import cached_property

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet


class HomePage(Page):
    def get_context(self, request, *args, **kwargs):
        # Imports locaux pour éviter tout souci d'ordre de chargement des apps.
        from network.models import NetworkMember
        from projects.models import MAX_FEATURED_PROJECTS, ProjectPage

        context = super().get_context(request, *args, **kwargs)

        context["featured_projects"] = (
            ProjectPage.objects.live()
            .public()
            .filter(featured=True)
            .select_related("thumbnail")
            .prefetch_related("tags")
            .order_by("-first_published_at")[:MAX_FEATURED_PROJECTS]
        )

        members = list(NetworkMember.objects.select_related("logo").all())
        context["network_members"] = members
        context["network_types"] = sorted({m.member_type for m in members})
        return context


class ReadOnlyPermissionPolicy(ModelPermissionPolicy):
    def user_has_permission(self, user, action):
        if action in ("add", "change", "delete"):
            return False
        return super().user_has_permission(user, action)


class ContactSubmission(models.Model):
    name = models.CharField("Nom", max_length=150)
    email = models.EmailField("Email")
    subject = models.CharField("Sujet", max_length=255)
    message = models.TextField("Message")
    created_at = models.DateTimeField("Date de soumission", auto_now_add=True)

    panels = [
        FieldPanel("name", read_only=True),
        FieldPanel("email", read_only=True),
        FieldPanel("subject", read_only=True),
        FieldPanel("message", read_only=True),
        FieldPanel("created_at", read_only=True),
    ]

    class Meta:
        verbose_name = "Demande de contact"
        verbose_name_plural = "Demandes de contact"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name} ({self.created_at:%d/%m/%Y})"


class ContactSubmissionViewSet(SnippetViewSet):
    model = ContactSubmission
    list_display = ["subject", "name", "email", "created_at"]
    list_filter = {"created_at": ["gte", "lte"]}
    search_fields = ["name", "email", "subject", "message"]
    ordering = ["-created_at"]
    icon = "mail"
    add_to_admin_menu = True
    menu_label = "Contacts"
    menu_order = 300
    inspect_view_enabled = True

    @cached_property
    def permission_policy(self):
        return ReadOnlyPermissionPolicy(self.model)


register_snippet(ContactSubmissionViewSet)
