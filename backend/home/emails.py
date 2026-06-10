"""Notifications email du formulaire de contact.

Suit la même logique de dégradation gracieuse que `turnstile.py` : si
`CONTACT_RECIPIENT_EMAIL` n'est pas configuré (dev, tests, CI), aucun mail
n'est envoyé. Les erreurs d'envoi sont journalisées sans jamais propager
d'exception : la demande de contact est déjà enregistrée en base, l'échec
de la notification ne doit pas casser la soumission côté visiteur.
"""

import logging

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_contact_notification(submission):
    """Notifie l'association d'une nouvelle demande de contact.

    Retourne True si un mail a été remis au backend d'envoi, False sinon
    (destinataire non configuré ou échec d'envoi).
    """
    recipient = settings.CONTACT_RECIPIENT_EMAIL
    if not recipient:
        return False

    submitted_at = timezone.localtime(submission.created_at)
    subject = f"[Contact Cultur'all] {submission.subject}"
    body = (
        "Nouvelle demande de contact reçue via le site.\n\n"
        f"Nom    : {submission.name}\n"
        f"Email  : {submission.email}\n"
        f"Sujet  : {submission.subject}\n"
        f"Date   : {submitted_at:%d/%m/%Y %H:%M}\n\n"
        f"Message :\n{submission.message}\n"
    )

    # reply_to = adresse du visiteur : répondre depuis la boîte de
    # l'association écrit directement à la personne qui a écrit.
    email = EmailMessage(
        subject=subject,
        body=body,
        to=[recipient],
        reply_to=[submission.email],
    )
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception("Échec de l'envoi de la notification de contact")
        return False
    return True
