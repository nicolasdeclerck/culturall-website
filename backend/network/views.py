from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import NetworkMember


@require_GET
def network_member_list(request):
    """Return all network members as JSON."""
    members = NetworkMember.objects.select_related("logo").all()
    data = [
        {
            "id": member.pk,
            "name": member.name,
            "member_type": member.member_type,
            "logo_url": (
                request.build_absolute_uri(
                    member.logo.get_rendition("fill-200x200").url
                )
                if member.logo
                else None
            ),
        }
        for member in members
    ]
    return JsonResponse(data, safe=False)
