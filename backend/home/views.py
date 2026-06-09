import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .forms import ContactForm
from .models import ContactSubmission


@csrf_exempt
@require_POST
def contact_submit(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "JSON invalide."}, status=400)

    errors = {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    subject = data.get("subject", "").strip()
    message = data.get("message", "").strip()

    if not name:
        errors["name"] = "Le nom est requis."
    if not email:
        errors["email"] = "L'email est requis."
    if not subject:
        errors["subject"] = "Le sujet est requis."
    if not message:
        errors["message"] = "Le message est requis."

    if errors:
        return JsonResponse({"errors": errors}, status=400)

    ContactSubmission.objects.create(
        name=name,
        email=email,
        subject=subject,
        message=message,
    )

    return JsonResponse({"message": "Votre message a bien été envoyé."}, status=201)


@require_http_methods(["GET", "POST"])
def contact_page(request):
    """Page de contact rendue côté serveur, avec soumission HTMX.

    Remplace le composant React `ContactForm.tsx`. En POST HTMX, renvoie le
    partial à swapper dans `#form-container` (succès ou formulaire ré-affiché
    avec ses erreurs). En l'absence de JS/HTMX, la page complète est re-rendue
    (amélioration progressive). L'endpoint JSON `contact_submit` reste en place
    tant que Next.js tourne ; il sera retiré en Phase 5.
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
