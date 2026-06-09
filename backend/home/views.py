from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_safe

from .forms import ContactForm
from .models import ContactSubmission, HomePage


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
        if form.is_valid():
            ContactSubmission.objects.create(**form.cleaned_data)
            if request.htmx:
                return render(request, "home/_contact_success.html")
            return render(request, "home/contact_page.html", {"success": True})

        if request.htmx:
            return render(request, "home/_contact_form.html", {"form": form})
        return render(request, "home/contact_page.html", {"form": form})

    return render(request, "home/contact_page.html", {"form": ContactForm()})
