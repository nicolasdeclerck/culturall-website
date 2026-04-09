import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

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
