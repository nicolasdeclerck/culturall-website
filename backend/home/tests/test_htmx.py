"""Socle HTMX — vérifie que django-htmx est câblé et que `request.htmx`
est exploitable depuis une vue (cf. ticket Phase 0 de la migration Wagtail).
"""

from django.conf import settings
from django.test import RequestFactory
from django_htmx.middleware import HtmxMiddleware


class TestHtmxFoundation:
    def test_middleware_is_installed(self):
        assert "django_htmx.middleware.HtmxMiddleware" in settings.MIDDLEWARE

    def test_request_htmx_falsy_without_header(self):
        captured = {}

        def view(request):
            captured["htmx"] = bool(request.htmx)
            return "ok"

        HtmxMiddleware(view)(RequestFactory().get("/"))
        assert captured["htmx"] is False

    def test_request_htmx_truthy_with_header(self):
        captured = {}

        def view(request):
            captured["htmx"] = bool(request.htmx)
            return "ok"

        HtmxMiddleware(view)(RequestFactory().get("/", HTTP_HX_REQUEST="true"))
        assert captured["htmx"] is True
