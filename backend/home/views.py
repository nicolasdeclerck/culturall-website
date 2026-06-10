from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_safe

from .emails import send_contact_notification
from .forms import ContactForm
from .models import ContactSubmission, HomePage
from .turnstile import verify_turnstile


def _client_ip(request):
    """IP de l'appelant en tenant compte d'un éventuel proxy (X-Forwarded-For)."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@require_safe
def home_page(request):
    """Page d'accueil rendue côté serveur (vidéo landing + projets à la une + réseau)."""
    page = HomePage.objects.live().first()
    if page is None:
        raise Http404("Page d'accueil introuvable")
    return page.serve(request)


@require_http_methods(["GET", "HEAD", "POST"])
def contact_page(request):
    """Page de contact rendue côté serveur, avec soumission HTMX.

    En POST HTMX, renvoie le partial à swapper dans `#form-container` (succès
    ou formulaire ré-affiché avec ses erreurs). En l'absence de JS/HTMX, la
    page complète est re-rendue (amélioration progressive).
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        form_valid = form.is_valid()
        human = verify_turnstile(
            request.POST.get("cf-turnstile-response", ""), _client_ip(request)
        )

        if form_valid and human:
            submission = ContactSubmission.objects.create(**form.cleaned_data)
            # Notifie l'association. L'échec d'envoi est absorbé par le
            # helper : la demande est déjà persistée, on n'interrompt jamais
            # le parcours visiteur pour un problème de serveur mail.
            send_contact_notification(submission)
            if request.htmx:
                return render(request, "home/_contact_success.html")
            return render(request, "home/contact_page.html", {"success": True})

        if not human:
            form.add_error(None, "La vérification anti-robot a échoué. Merci de réessayer.")

        if request.htmx:
            return render(request, "home/_contact_form.html", {"form": form})
        return render(request, "home/contact_page.html", {"form": form})

    return render(request, "home/contact_page.html", {"form": ContactForm()})
