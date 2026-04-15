from django.http import JsonResponse
from wagtail.models import Site

from .models import SiteSettings


def site_settings_view(request):
    """Returns public site settings (logo URL)."""
    site = Site.find_for_request(request)
    settings = SiteSettings.for_site(site)

    logo_url = None
    if settings.logo:
        logo_url = settings.logo.get_rendition("max-300x80").url

    return JsonResponse({"logo_url": logo_url})
