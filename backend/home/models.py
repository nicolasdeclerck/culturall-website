"""
Home app — point d'entrée Wagtail.

Pour l'instant ne contient qu'un HomePage minimal. Quand tu seras prêt à
basculer le routing racine sur Wagtail, lance :

    python manage.py makemigrations home
    python manage.py migrate

…puis crée une page HomePage via /admin/ et décommente la route catch-all
dans config/urls.py.
"""

from django.db import models
from wagtail.models import Page


class HomePage(Page):
    pass


class ContactSubmission(models.Model):
    name = models.CharField("Nom", max_length=150)
    email = models.EmailField("Email")
    subject = models.CharField("Sujet", max_length=255)
    message = models.TextField("Message")
    created_at = models.DateTimeField("Date de soumission", auto_now_add=True)

    class Meta:
        verbose_name = "Demande de contact"
        verbose_name_plural = "Demandes de contact"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name} ({self.created_at:%d/%m/%Y})"
