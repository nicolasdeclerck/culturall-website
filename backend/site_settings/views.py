from django.http import JsonResponse
from django.views.decorators.http import require_GET
from wagtail.models import Site

from .models import SiteSettings


@require_GET
def site_settings(request):
    """Return public site settings consumed by the frontend home page."""
    site = Site.find_for_request(request)
    settings = SiteSettings.for_site(site)

    background_video_url = None
    if settings.background_video:
        background_video_url = request.build_absolute_uri(
            settings.background_video.url
        )

    background_video_poster_url = None
    if settings.background_video_poster:
        background_video_poster_url = request.build_absolute_uri(
            settings.background_video_poster.get_rendition("max-1920x1080").url
        )

    return JsonResponse(
        {
            "background_video_url": background_video_url,
            "background_video_poster_url": background_video_poster_url,
        }
    )
