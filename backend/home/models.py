"""
Home app — point d'entrée Wagtail.

La `HomePage` est créée par la data migration `0003_seed_home_page` et sert
de racine à l'arbre Wagtail (parent direct de `BlogIndexPage` et, à terme,
des autres pages d'accueil de section). Le `Site` Wagtail par défaut pointe
sur cette `HomePage`.

Le rendu HTML est fait côté serveur par Wagtail : toutes les pages (accueil,
projets, blog, pages statiques, contact) sont servies nativement par le
catch-all Wagtail (`config/urls.py`). La `HomePage` est le root page du `Site`
Wagtail par défaut et est donc servie sur `/`.
"""

from functools import cached_property

from django.db import models
from django.http import HttpResponseNotAllowed
from django.shortcuts import render
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.permission_policies import ModelPermissionPolicy
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from home.blocks import CustomSectionBlock
from home.forms import ContactForm
from home.turnstile import verify_turnstile


class HomePage(Page):
    hero_title = models.CharField(
        "Titre principal",
        max_length=255,
        default="Cultur'all",
        help_text="Titre affiché en grand sur la vidéo d'accueil.",
    )
    hero_subtitle = models.TextField(
        "Sous-titre",
        blank=True,
        default=(
            "Création et Production de contenus audiovisuels à Lille : "
            "documentaires, clips, captations et contenus dans les "
            "Hauts-de-France"
        ),
        help_text="Texte de description affiché sous le titre principal.",
    )

    top_custom_section = StreamField(
        CustomSectionBlock(),
        blank=True,
        verbose_name="Section personnalisable (au-dessus du réseau)",
        help_text=(
            "Zone libre affichée au-dessus de la section « Notre Réseau ». "
            "Ajoutez les blocs souhaités, dans l'ordre voulu."
        ),
    )

    custom_section = StreamField(
        CustomSectionBlock(),
        blank=True,
        verbose_name="Section personnalisable (sous le réseau)",
        help_text=(
            "Zone libre affichée sous la section « Notre Réseau ». "
            "Ajoutez les blocs souhaités, dans l'ordre voulu."
        ),
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_title"),
        FieldPanel("hero_subtitle"),
        FieldPanel("top_custom_section"),
        FieldPanel("custom_section"),
    ]

    def get_context(self, request, *args, **kwargs):
        # Import local pour éviter tout souci d'ordre de chargement des apps.
        from network.models import NetworkMember

        context = super().get_context(request, *args, **kwargs)

        members = list(NetworkMember.objects.select_related("logo").all())
        context["network_members"] = members
        context["network_types"] = sorted({m.member_type for m in members})
        return context


def _client_ip(request):
    """IP de l'appelant en tenant compte d'un éventuel proxy (X-Forwarded-For)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class ContactPage(Page):
    """Page de contact, servie nativement par Wagtail.

    Le rendu (template + `get_context`) est natif ; `serve()` ajoute la
    gestion de la soumission POST du formulaire : vérification Cloudflare
    Turnstile puis enregistrement d'une `ContactSubmission`. En requête HTMX,
    seul le partial à swapper dans `#form-container` est renvoyé (succès ou
    formulaire ré-affiché avec ses erreurs) ; sinon la page complète est
    re-rendue (amélioration progressive).
    """

    template = "home/contact_page.html"

    parent_page_types = ["home.HomePage"]
    subpage_types = []
    max_count = 1

    class Meta:
        verbose_name = "Page de contact"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context.setdefault("form", ContactForm())
        return context

    def serve(self, request, *args, **kwargs):
        if request.method == "POST":
            return self._handle_submission(request)
        if request.method not in ("GET", "HEAD"):
            return HttpResponseNotAllowed(["GET", "HEAD", "POST"])
        return super().serve(request, *args, **kwargs)

    def _handle_submission(self, request):
        form = ContactForm(request.POST)
        form_valid = form.is_valid()
        human = verify_turnstile(
            request.POST.get("cf-turnstile-response", ""), _client_ip(request)
        )

        if form_valid and human:
            ContactSubmission.objects.create(**form.cleaned_data)
            if request.htmx:
                return render(request, "home/_contact_success.html", {"page": self})
            return render(
                request, "home/contact_page.html", {"page": self, "success": True}
            )

        if not human:
            form.add_error(None, "La vérification anti-robot a échoué. Merci de réessayer.")

        if request.htmx:
            return render(request, "home/_contact_form.html", {"page": self, "form": form})
        return render(request, "home/contact_page.html", {"page": self, "form": form})


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
